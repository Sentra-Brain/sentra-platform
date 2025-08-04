# tests/features/knowledge/test_rag_service.py

import pytest
from unittest.mock import Mock, AsyncMock, patch
from uuid import uuid4
import httpx

from sentra_brain_api.features.knowledge.rag_service import RAGQueryService


class TestRAGService:
    """Test the RAG query service."""

    @pytest.fixture
    def rag_service(self):
        """Create RAG service instance."""
        return RAGQueryService()

    @pytest.fixture
    def mock_embedding_model(self):
        """Mock sentence transformer model."""
        model = Mock()
        model.encode.return_value = [0.1, 0.2, 0.3]  # Mock embedding vector
        return model

    @patch.dict('os.environ', {'CHROMA_URL': 'http://test-chroma:8000'})
    @patch('httpx.AsyncClient')
    @pytest.mark.asyncio
    async def test_search_documents_success(self, mock_client_class, rag_service, mock_embedding_model):
        """Test successful document search."""
        # Mock the embedding model
        with patch.object(rag_service, '_get_embedding_model', return_value=mock_embedding_model):
            # Mock HTTP client
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            # Mock ChromaDB response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'ids': [['doc1_chunk_0', 'doc2_chunk_1']],
                'documents': [['First chunk content', 'Second chunk content']],
                'metadatas': [[
                    {'filename': 'doc1.pdf', 'chunk_index': 0, 'document_id': 'doc1'},
                    {'filename': 'doc2.pdf', 'chunk_index': 1, 'document_id': 'doc2'}
                ]],
                'distances': [[0.1, 0.3]]
            }
            mock_client.post.return_value = mock_response
            
            # Perform search
            results = await rag_service.search_documents(
                query="test query",
                limit=5
            )
            
            # Verify results
            assert len(results) == 2
            assert results[0]['chunk_id'] == 'doc1_chunk_0'
            assert results[0]['content'] == 'First chunk content'
            assert results[0]['relevance_score'] == 0.9  # 1.0 - 0.1
            assert results[1]['relevance_score'] == 0.7  # 1.0 - 0.3
            
            # Verify HTTP call
            mock_client.post.assert_called_once()
            call_args = mock_client.post.call_args
            assert 'http://test-chroma:8000/api/v1/collections/document_chunks/query' in call_args[0]
            assert call_args[1]['json']['query_embeddings'] == [[0.1, 0.2, 0.3]]
            assert call_args[1]['json']['n_results'] == 5

    @patch.dict('os.environ', {'CHROMA_URL': 'http://test-chroma:8000'})
    @patch('httpx.AsyncClient')
    @pytest.mark.asyncio
    async def test_search_documents_with_knowledge_source_filter(self, mock_client_class, rag_service, mock_embedding_model):
        """Test search with knowledge source filter."""
        knowledge_source_id = uuid4()
        
        with patch.object(rag_service, '_get_embedding_model', return_value=mock_embedding_model):
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'ids': [[]],
                'documents': [[]],
                'metadatas': [[]],
                'distances': [[]]
            }
            mock_client.post.return_value = mock_response
            
            # Perform search with filter
            await rag_service.search_documents(
                query="test query",
                knowledge_source_id=knowledge_source_id,
                limit=5
            )
            
            # Verify filter was applied
            call_args = mock_client.post.call_args
            assert call_args[1]['json']['where'] == {'knowledge_source_id': str(knowledge_source_id)}

    @patch.dict('os.environ', {'CHROMA_URL': 'http://test-chroma:8000'})
    @patch('httpx.AsyncClient')
    @pytest.mark.asyncio
    async def test_search_documents_http_error(self, mock_client_class, rag_service, mock_embedding_model):
        """Test handling of HTTP errors."""
        with patch.object(rag_service, '_get_embedding_model', return_value=mock_embedding_model):
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            # Mock HTTP error
            mock_response = Mock()
            mock_response.status_code = 500
            mock_response.text = "Internal Server Error"
            mock_client.post.return_value = mock_response
            
            # Perform search
            results = await rag_service.search_documents(query="test query")
            
            # Should return empty list on error
            assert results == []

    @patch.object(RAGQueryService, 'search_documents')
    @pytest.mark.asyncio
    async def test_get_context_for_query_success(self, mock_search, rag_service):
        """Test successful context generation."""
        # Mock search results
        mock_chunks = [
            {
                'content': 'This is the first chunk about AI.',
                'metadata': {'filename': 'ai_intro.pdf', 'chunk_index': 0}
            },
            {
                'content': 'This is the second chunk about machine learning.',
                'metadata': {'filename': 'ml_guide.pdf', 'chunk_index': 1}
            }
        ]
        mock_search.return_value = mock_chunks
        
        # Generate context
        context = await rag_service.get_context_for_query(
            query="What is AI?",
            max_tokens=1000
        )
        
        # Verify context format
        assert "Relevant information from your knowledge base:" in context
        assert "Source: ai_intro.pdf (chunk 0)" in context
        assert "Source: ml_guide.pdf (chunk 1)" in context
        assert "This is the first chunk about AI." in context
        assert "This is the second chunk about machine learning." in context
        
        # Verify search was called
        mock_search.assert_called_once_with(
            query="What is AI?",
            knowledge_source_id=None,
            limit=20
        )

    @patch.object(RAGQueryService, 'search_documents')
    @pytest.mark.asyncio
    async def test_get_context_for_query_empty_results(self, mock_search, rag_service):
        """Test context generation with empty search results."""
        mock_search.return_value = []
        
        context = await rag_service.get_context_for_query(query="test query")
        
        assert context == ""

    @patch.object(RAGQueryService, 'search_documents')
    @pytest.mark.asyncio
    async def test_get_context_for_query_token_limiting(self, mock_search, rag_service):
        """Test that context generation respects token limits."""
        # Create a chunk with many characters (simulating large content)
        large_content = "A" * 8000  # 8000 characters ≈ 2000 tokens
        
        mock_chunks = [
            {
                'content': large_content,
                'metadata': {'filename': 'large_doc.pdf', 'chunk_index': 0}
            },
            {
                'content': 'This smaller chunk should not be included.',
                'metadata': {'filename': 'small_doc.pdf', 'chunk_index': 0}
            }
        ]
        mock_search.return_value = mock_chunks
        
        # Generate context with low token limit
        context = await rag_service.get_context_for_query(
            query="test query",
            max_tokens=1000  # Should only fit first chunk partially
        )
        
        # Should include first chunk but not second
        assert "large_doc.pdf" in context
        assert "small_doc.pdf" not in context

    @patch.dict('os.environ', {'EMBEDDING_MODEL': 'test-model'})
    @patch('sentence_transformers.SentenceTransformer')
    def test_get_embedding_model_lazy_loading(self, mock_transformer_class, rag_service):
        """Test lazy loading of embedding model."""
        mock_model = Mock()
        mock_transformer_class.return_value = mock_model
        
        # First call should load the model
        model1 = rag_service._get_embedding_model()
        assert model1 == mock_model
        mock_transformer_class.assert_called_once_with('test-model')
        
        # Second call should reuse the same model
        model2 = rag_service._get_embedding_model()
        assert model2 == mock_model
        assert model1 is model2
        # Should not call constructor again
        assert mock_transformer_class.call_count == 1

    @patch('httpx.AsyncClient')
    @pytest.mark.asyncio
    async def test_search_documents_exception_handling(self, mock_client_class, rag_service, mock_embedding_model):
        """Test exception handling in search_documents."""
        with patch.object(rag_service, '_get_embedding_model', return_value=mock_embedding_model):
            # Mock client to raise exception
            mock_client_class.side_effect = Exception("Connection error")
            
            # Should not raise exception but return empty list
            results = await rag_service.search_documents(query="test query")
            assert results == []

    @pytest.mark.asyncio
    async def test_get_context_for_query_exception_handling(self, rag_service):
        """Test exception handling in get_context_for_query."""
        with patch.object(rag_service, 'search_documents', side_effect=Exception("Search error")):
            # Should not raise exception but return empty string
            context = await rag_service.get_context_for_query(query="test query")
            assert context == ""