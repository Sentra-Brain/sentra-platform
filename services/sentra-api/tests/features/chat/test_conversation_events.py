import pytest
import json
from unittest.mock import AsyncMock, Mock
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sentra_brain_api.core.conversation_engine.models.input_model import ConversationRequest
from sentra_brain_api.core.conversation_engine.models.output_model import ConversationEvent
from sentra_brain_api.features.chat.controller import ChatController
from sentra_brain_api.crosscutting.authorization import get_authenticated_user
from sentra_core.domain.entities.user_entity import UserEntity
import uuid


@pytest.fixture
def mock_user():
    return UserEntity(id=uuid.uuid4(), username="testuser")


@pytest.fixture
def mock_conversation_engine():
    engine = Mock()
    # Mock the async generator that yields ConversationEvent objects
    async def mock_run(request):
        # Simulate step events for RAG
        yield ConversationEvent(
            type="step_start",
            step_id="rag_search",
            label="Searching knowledge base",
            status="running"
        )
        yield ConversationEvent(
            type="step_end", 
            step_id="rag_search",
            status="done",
            meta={"num_chunks": 5}
        )
        # Simulate message delta events
        yield ConversationEvent(type="message_delta", content="Hello")
        yield ConversationEvent(type="message_delta", content=" World")
        # Simulate final message event
        yield ConversationEvent(type="message_final", content="Hello World")
    
    engine.run = mock_run
    return engine


@pytest.fixture
def test_app(mock_conversation_engine, mock_user):
    app = FastAPI()
    
    # Mock app state
    app_state = Mock()
    app_state.conversation_engine = mock_conversation_engine
    app.state._sentra = app_state
    
    # Override authentication dependency
    app.dependency_overrides[get_authenticated_user] = lambda: mock_user
    
    # Add the chat controller routes
    chat_controller = ChatController()
    app.include_router(chat_controller.router, prefix="/chat")
    
    return app


def test_conversation_events_sse_format(test_app):
    """Test that ConversationEvent objects are properly serialized as SSE events"""
    with TestClient(test_app) as client:
        request_data = {
            "conversation_id": str(uuid.uuid4()),
            "message_id": str(uuid.uuid4()),
            "response_message_id": str(uuid.uuid4()),
            "content": "Test message",
            "context_source_ids": ["source1"],
            "context_document_ids": []
        }
        
        response = client.post("/chat/send", json=request_data)
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream; charset=utf-8"
        
        # Parse the SSE response
        lines = response.text.strip().split('\n')
        events = []
        
        for line in lines:
            if line.startswith('data: '):
                data = line[6:]  # Remove 'data: ' prefix
                try:
                    event = json.loads(data)
                    events.append(event)
                except json.JSONDecodeError:
                    continue
        
        # Verify we got the expected events
        assert len(events) == 5
        
        # Verify step events
        assert events[0]["type"] == "step_start"
        assert events[0]["step_id"] == "rag_search"
        assert events[0]["label"] == "Searching knowledge base"
        assert events[0]["status"] == "running"
        assert "timestamp" in events[0]
        
        assert events[1]["type"] == "step_end"
        assert events[1]["step_id"] == "rag_search"
        assert events[1]["status"] == "done"
        assert events[1]["meta"]["num_chunks"] == 5
        
        # Verify message events
        assert events[2]["type"] == "message_delta"
        assert events[2]["content"] == "Hello"
        
        assert events[3]["type"] == "message_delta"
        assert events[3]["content"] == " World"
        
        assert events[4]["type"] == "message_final"
        assert events[4]["content"] == "Hello World"


def test_conversation_events_without_rag(test_app, mock_conversation_engine):
    """Test that events work correctly without RAG context"""
    # Mock engine to not emit step events when no context
    async def mock_run_no_rag(request):
        yield ConversationEvent(type="message_delta", content="Response")
        yield ConversationEvent(type="message_final", content="Response")
    
    mock_conversation_engine.run = mock_run_no_rag
    
    with TestClient(test_app) as client:
        request_data = {
            "conversation_id": str(uuid.uuid4()),
            "message_id": str(uuid.uuid4()),
            "response_message_id": str(uuid.uuid4()),
            "content": "Test message"
            # No context_source_ids or context_document_ids
        }
        
        response = client.post("/chat/send", json=request_data)
        
        assert response.status_code == 200
        
        # Parse events
        lines = response.text.strip().split('\n')
        events = []
        
        for line in lines:
            if line.startswith('data: '):
                data = line[6:]
                try:
                    event = json.loads(data)
                    events.append(event)
                except json.JSONDecodeError:
                    continue
        
        # Should only have message events, no step events
        assert len(events) == 2
        assert all(event["type"].startswith("message_") for event in events)