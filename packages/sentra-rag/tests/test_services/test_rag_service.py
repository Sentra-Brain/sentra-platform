import pytest
from unittest.mock import AsyncMock, Mock, patch
from uuid import UUID
from sentra.rag.services.rag_service import RAGQueryService


class TestRAGQueryService:

    @pytest.fixture
    def rag_service(self):
        """Create a RAGQueryService instance for testing."""
        with patch('sentra_rag.services.rag_service.get_embedding_provider'), \
             patch('sentra_rag.services.rag_service.VectorStoreService'):
            return RAGQueryService()

    @pytest.mark.asyncio
    async def test_search_documents_success(self, rag_service):
        """Test successful document search."""
        # Mock embedding provider
        mock_embedding = [0.1, 0.2, 0.3]
        rag_service.embedding_provider.embed_query.return_value = mock_embedding
        
        # Mock vector store response
        mock_results = {
            'ids': [['chunk1', 'chunk2']],
            'documents': [['content1', 'content2']],
            'metadatas': [[{'filename': 'file1.txt'}, {'filename': 'file2.txt'}]],
            'distances': [[0.1, 0.2]]
        }
        rag_service.vector_store.query_similar_documents = AsyncMock(return_value=mock_results)
        
        # Test
        results = await rag_service.search_documents("test query", limit=5)
        
        # Assertions
        assert len(results) == 2
        assert results[0]['chunk_id'] == 'chunk1'
        assert results[0]['content'] == 'content1'
        assert results[0]['relevance_score'] == 0.9  # 1.0 - 0.1
        
        rag_service.embedding_provider.embed_query.assert_called_once_with("test query")
        rag_service.vector_store.query_similar_documents.assert_called_once_with(
            query_embedding=mock_embedding,
            knowledge_source_id=None,
            limit=5
        )

    @pytest.mark.asyncio
    async def test_search_documents_with_knowledge_source(self, rag_service):
        """Test document search with knowledge source filter."""
        knowledge_source_id = UUID('12345678-1234-5678-9012-123456789012')
        mock_embedding = [0.1, 0.2, 0.3]
        rag_service.embedding_provider.embed_query.return_value = mock_embedding
        rag_service.vector_store.query_similar_documents = AsyncMock(return_value={'ids': [[]]})
        
        await rag_service.search_documents("test query", knowledge_source_id=knowledge_source_id)
        
        rag_service.vector_store.query_similar_documents.assert_called_once_with(
            query_embedding=mock_embedding,
            knowledge_source_id=knowledge_source_id,
            limit=10  # default limit
        )

    @pytest.mark.asyncio
    async def test_get_context_for_query_success(self, rag_service):
        """Test successful context generation."""
        # Mock search_documents to return chunks
        mock_chunks = [
            {
                'content': 'This is content 1',
                'metadata': {'filename': 'file1.txt', 'chunk_index': 0}
            },
            {
                'content': 'This is content 2',
                'metadata': {'filename': 'file2.txt', 'chunk_index': 1}
            }
        ]
        
        with patch.object(rag_service, 'search_documents', new_callable=AsyncMock) as mock_search:
            mock_search.return_value = mock_chunks
            
            context = await rag_service.get_context_for_query("test query", max_tokens=1000)
            
            assert "Relevant information from your knowledge base:" in context
            assert "Source: file1.txt (chunk 0)" in context
            assert "This is content 1" in context
            assert "Source: file2.txt (chunk 1)" in context
            assert "This is content 2" in context
            
            mock_search.assert_called_once_with(
                query="test query",
                knowledge_source_id=None,
                limit=20
            )

    @pytest.mark.asyncio
    async def test_get_context_for_query_empty_results(self, rag_service):
        """Test context generation with no search results."""
        with patch.object(rag_service, 'search_documents', new_callable=AsyncMock) as mock_search:
            mock_search.return_value = []
            
            context = await rag_service.get_context_for_query("test query")
            
            assert context == ""