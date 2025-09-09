import pytest
from unittest.mock import AsyncMock, Mock, patch
from uuid import UUID
from sentra.rag.services.rag_service import RAGQueryService


class TestRAGQueryService:
    @pytest.fixture
    def rag_service(self):
        with patch("sentra.rag.services.rag_service.get_embedding_provider") as mock_embed_provider, \
            patch("sentra.rag.services.rag_service.get_vector_store_service") as mock_vector_store:
            mock_embed_provider.return_value = Mock() 
            mock_vector_store.return_value = AsyncMock()
            return RAGQueryService()

    @pytest.mark.asyncio
    async def test_search_documents_success(self, rag_service):
        mock_embedding = [0.1, 0.2, 0.3]
        rag_service.embedding_provider.embed_query.return_value = mock_embedding

        mock_results = [
            {"id": "chunk1", "document": "content1", "metadata": {"filename": "file1.txt"}, "distance": 0.1},
            {"id": "chunk2", "document": "content2", "metadata": {"filename": "file2.txt"}, "distance": 0.2},
        ]
        rag_service.vector_store.query_similar_chunks = AsyncMock(return_value=mock_results)

        results = await rag_service.search_documents("test query", limit=5)

        assert len(results) == 2
        assert results[0]["chunk_id"] == "chunk1"
        assert results[0]["content"] == "content1"
        assert results[0]["relevance_score"] == 0.9

        rag_service.embedding_provider.embed_query.assert_called_once_with("test query")
        rag_service.vector_store.query_similar_chunks.assert_called_once_with(
            query_embedding=mock_embedding, knowledge_source_id=None, limit=5
        )

    @pytest.mark.asyncio
    async def test_search_documents_with_knowledge_source(self, rag_service):
        knowledge_source_id = UUID("12345678-1234-5678-9012-123456789012")
        mock_embedding = [0.1, 0.2, 0.3]
        rag_service.embedding_provider.embed_query.return_value = mock_embedding
        rag_service.vector_store.query_similar_chunks = AsyncMock(return_value=[])

        await rag_service.search_documents("test query", knowledge_source_id=knowledge_source_id)

        rag_service.vector_store.query_similar_chunks.assert_called_once_with(
            query_embedding=mock_embedding, knowledge_source_id=knowledge_source_id, limit=10
        )
