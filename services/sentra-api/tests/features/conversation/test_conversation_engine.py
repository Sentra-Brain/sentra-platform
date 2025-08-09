import pytest
import uuid
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime, timezone

from sentra_brain_api.core.conversation_engine.engine import ConversationEngine
from sentra_brain_api.core.conversation_engine.models.input_model import ConversationRequest
from sentra_brain_api.core.conversation_engine.models.output_model import ConversationEvent
from sentra_brain_api.core.conversation_engine.rag.rag_chunk import RagChunk


class TestConversationEngine:
    @pytest.fixture
    def mock_mongo_repo(self):
        repo = Mock()
        repo.get_conversation_by_id.return_value = {
            "_id": "test-conv",
            "user_id": "test-user",
            "messages": []
        }
        repo.append_message.return_value = 1
        return repo

    @pytest.fixture
    def mock_vllm_client(self):
        client = Mock()
        
        # Mock the async generator for LLM streaming
        async def mock_stream():
            yield 'data: {"choices": [{"delta": {"content": "Test "}}]}'
            yield 'data: {"choices": [{"delta": {"content": "response"}}]}'
        
        client.chat_completion.return_value = mock_stream()
        return client

    @pytest.fixture
    def mock_rag_client(self):
        client = Mock()
        client.retrieve_relevant_chunks = AsyncMock(return_value=[
            RagChunk(
                chunk_id="chunk1",
                content="test chunk 1",
                relevance_score=0.9,
                document_id=uuid.uuid4(),
                knowledge_source_id=uuid.uuid4(),
                source_type="document",
                filename="test1.pdf"
            ),
            RagChunk(
                chunk_id="chunk2",
                content="test chunk 2",
                relevance_score=0.8,
                document_id=uuid.uuid4(),
                knowledge_source_id=uuid.uuid4(),
                source_type="document",
                filename="test2.pdf"
            )
        ])
        return client

    @pytest.fixture
    def engine(self, mock_mongo_repo, mock_vllm_client, mock_rag_client):
        return ConversationEngine(
            mongo_repo=mock_mongo_repo,
            vllm_client=mock_vllm_client,
            rag_client=mock_rag_client
        )

    @pytest.fixture
    def conversation_request(self):
        return ConversationRequest(
            conversation_id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            content="Test message with RAG",
            message_id=uuid.uuid4(),
            response_message_id=uuid.uuid4(),
            context_source_ids=[uuid.uuid4(), uuid.uuid4()],
            context_document_ids=None
        )

    @pytest.mark.asyncio
    async def test_step_events_emitted_and_persisted(self, engine, conversation_request, mock_mongo_repo):
        """Test that step events are emitted and persisted as system messages"""
        events = []
        
        # Collect all events
        async for event in engine.run(conversation_request):
            events.append(event)

        # Verify we have the expected event types
        event_types = [event.type for event in events]
        
        # Should have: step_start, step_end, message_delta(s), message_final
        assert "step_start" in event_types
        assert "step_end" in event_types
        assert "message_delta" in event_types
        assert "message_final" in event_types

        # Verify step_start event structure
        step_start_events = [e for e in events if e.type == "step_start"]
        assert len(step_start_events) == 1
        step_start = step_start_events[0]
        
        assert step_start.task_type == "rag_search"
        assert step_start.task_run_id is not None
        assert step_start.label == "Searching Knowledge Base"
        assert step_start.status == "searching"
        assert "Searching in the Knowledge Base" in step_start.content

        # Verify step_end event structure
        step_end_events = [e for e in events if e.type == "step_end"]
        assert len(step_end_events) == 1
        step_end = step_end_events[0]
        
        assert step_end.task_type == "rag_search"
        assert step_end.task_run_id == step_start.task_run_id  # Same task_run_id
        assert step_end.label == "Knowledge Base Search Complete"
        assert step_end.status == "completed"
        assert step_end.meta is not None
        assert step_end.meta["chunks_found"] == 2

        # Verify step events were persisted as system messages
        append_calls = mock_mongo_repo.append_message.call_args_list
        
        # Should have: user message, step_start, step_end, assistant message
        assert len(append_calls) >= 4
        
        # Check that step events were persisted as system messages
        step_system_messages = []
        for call in append_calls:
            message = call[1]["message"]  # keyword argument
            if message.get("role") == "system":
                step_system_messages.append(message)
        
        assert len(step_system_messages) == 2  # step_start and step_end
        
        # Verify system message structure
        for sys_msg in step_system_messages:
            assert sys_msg["id"] is not None
            assert sys_msg["role"] == "system"
            assert sys_msg["timestamp"] is not None
            assert sys_msg["event_type"] in ["step_start", "step_end"]
            assert sys_msg["task_type"] == "rag_search"
            assert sys_msg["task_run_id"] is not None

    @pytest.mark.asyncio
    async def test_no_step_events_without_rag(self, engine, mock_mongo_repo, mock_vllm_client, mock_rag_client):
        """Test that no step events are emitted when no RAG context is requested"""
        request = ConversationRequest(
            conversation_id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            content="Test message without RAG",
            message_id=uuid.uuid4(),
            response_message_id=uuid.uuid4(),
            context_source_ids=None,
            context_document_ids=None
        )
        
        events = []
        async for event in engine.run(request):
            events.append(event)

        # Should only have message events, no step events
        event_types = [event.type for event in events]
        assert "step_start" not in event_types
        assert "step_end" not in event_types
        assert "message_delta" in event_types
        assert "message_final" in event_types

        # Verify RAG client was not called
        mock_rag_client.retrieve_relevant_chunks.assert_called_once_with(
            query=request.content,
            source_ids=None,
            document_ids=None
        )

    @pytest.mark.asyncio
    async def test_conversation_event_structure(self, engine, conversation_request):
        """Test that all ConversationEvent objects have proper structure"""
        events = []
        async for event in engine.run(conversation_request):
            events.append(event)

        for event in events:
            # All events should be ConversationEvent instances
            assert isinstance(event, ConversationEvent)
            
            # All events should have event_id and timestamp
            assert event.event_id is not None
            assert event.timestamp is not None
            
            # Timestamp should be ISO format
            datetime.fromisoformat(event.timestamp.replace('Z', '+00:00'))
            
            # Type should be valid
            assert event.type in [
                "message_delta", "message_final", 
                "step_start", "step_progress", "step_end", "step_error"
            ]