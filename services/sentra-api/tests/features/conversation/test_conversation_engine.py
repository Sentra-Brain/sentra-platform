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
            llm_client=mock_vllm_client,
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