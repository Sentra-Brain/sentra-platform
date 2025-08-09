import pytest
import uuid
import json
from unittest.mock import Mock, AsyncMock, patch
from fastapi import FastAPI
from fastapi.testclient import TestClient

from sentra_brain_api.features.chat.controller import ChatController
from sentra_brain_api.core.conversation_engine.models.input_model import ConversationRequest
from sentra_brain_api.core.conversation_engine.models.output_model import ConversationEvent
from sentra_brain_api.core.conversation_engine.rag.rag_chunk import RagChunk
from sentra_core.domain.entities.user_entity import UserEntity
from sentra_brain_api.crosscutting.authorization import get_authenticated_user


class TestChatControllerSSE:
    @pytest.fixture
    def mock_user(self):
        return UserEntity(id=uuid.uuid4(), username="testuser")

    @pytest.fixture
    def mock_app_state(self):
        app_state = Mock()
        
        # Mock conversation engine
        engine = Mock()
        
        # Create a mock async generator that yields ConversationEvent objects
        async def mock_engine_run(request):
            # Emit step events for RAG if context is requested
            if request.context_source_ids:
                task_run_id = uuid.uuid4().hex
                
                yield ConversationEvent(
                    type="step_start",
                    task_type="rag_search",
                    task_run_id=task_run_id,
                    label="Searching Knowledge Base",
                    status="searching",
                    content="💡 Searching in the Knowledge Base..."
                )
                
                yield ConversationEvent(
                    type="step_end",
                    task_type="rag_search",
                    task_run_id=task_run_id,
                    label="Knowledge Base Search Complete",
                    status="completed",
                    content="Found 2 relevant chunks",
                    meta={"chunks_found": 2}
                )
            
            # Emit message events
            yield ConversationEvent(type="message_delta", content="Hello ")
            yield ConversationEvent(type="message_delta", content="world!")
            yield ConversationEvent(type="message_final", content="")
        
        engine.run = mock_engine_run
        app_state.conversation_engine = engine
        
        return app_state

    @pytest.fixture
    def client(self, mock_user, mock_app_state):
        app = FastAPI()
        controller = ChatController()
        app.include_router(controller.router, prefix="/chat")
        
        # Mock dependencies
        app.dependency_overrides[get_authenticated_user] = lambda: mock_user
        
        # Mock app state
        app.state._sentra = mock_app_state
        
        return TestClient(app)

    def test_sse_streaming_with_step_events(self, client):
        """Test that SSE streaming works correctly with step events"""
        payload = {
            "conversation_id": str(uuid.uuid4()),
            "content": "Test message with RAG",
            "message_id": str(uuid.uuid4()),
            "response_message_id": str(uuid.uuid4()),
            "context_source_ids": [str(uuid.uuid4()), str(uuid.uuid4())]
        }
        
        response = client.post("/chat/send", json=payload)
        
        # Verify response is SSE
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream; charset=utf-8"
        
        # Parse SSE events
        events = []
        for line in response.text.split("\n"):
            if line.startswith("data: "):
                event_data = line[6:]  # Remove "data: " prefix
                if event_data.strip():  # Skip empty lines
                    try:
                        event = json.loads(event_data)
                        events.append(event)
                    except json.JSONDecodeError:
                        pass  # Skip malformed events
        
        # Verify we got events
        assert len(events) > 0
        
        # Check event types
        event_types = [event.get("type") for event in events]
        assert "step_start" in event_types
        assert "step_end" in event_types
        assert "message_delta" in event_types
        assert "message_final" in event_types
        
        # Verify step events structure
        step_start_events = [e for e in events if e.get("type") == "step_start"]
        assert len(step_start_events) == 1
        step_start = step_start_events[0]
        
        assert step_start["task_type"] == "rag_search"
        assert step_start["task_run_id"] is not None
        assert step_start["label"] == "Searching Knowledge Base"
        assert step_start["status"] == "searching"
        assert "event_id" in step_start
        assert "timestamp" in step_start
        
        # Verify step_end event
        step_end_events = [e for e in events if e.get("type") == "step_end"]
        assert len(step_end_events) == 1
        step_end = step_end_events[0]
        
        assert step_end["task_type"] == "rag_search"
        assert step_end["task_run_id"] == step_start["task_run_id"]
        assert step_end["label"] == "Knowledge Base Search Complete"
        assert step_end["status"] == "completed"
        assert step_end["meta"]["chunks_found"] == 2

    def test_sse_streaming_without_step_events(self, client):
        """Test that SSE streaming works correctly without step events"""
        payload = {
            "conversation_id": str(uuid.uuid4()),
            "content": "Test message without RAG",
            "message_id": str(uuid.uuid4()),
            "response_message_id": str(uuid.uuid4()),
            "context_source_ids": None
        }
        
        response = client.post("/chat/send", json=payload)
        
        # Verify response is SSE
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream; charset=utf-8"
        
        # Parse SSE events
        events = []
        for line in response.text.split("\n"):
            if line.startswith("data: "):
                event_data = line[6:]  # Remove "data: " prefix
                if event_data.strip():  # Skip empty lines
                    try:
                        event = json.loads(event_data)
                        events.append(event)
                    except json.JSONDecodeError:
                        pass  # Skip malformed events
        
        # Verify we got events
        assert len(events) > 0
        
        # Check event types - should only have message events
        event_types = [event.get("type") for event in events]
        assert "step_start" not in event_types
        assert "step_end" not in event_types
        assert "message_delta" in event_types
        assert "message_final" in event_types
        
        # Verify all events have required fields
        for event in events:
            assert "event_id" in event
            assert "timestamp" in event
            assert "type" in event

    def test_sse_content_type_header(self, client):
        """Test that the correct content-type header is set"""
        payload = {
            "conversation_id": str(uuid.uuid4()),
            "content": "Test message",
            "message_id": str(uuid.uuid4()),
            "response_message_id": str(uuid.uuid4())
        }
        
        response = client.post("/chat/send", json=payload)
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream; charset=utf-8"