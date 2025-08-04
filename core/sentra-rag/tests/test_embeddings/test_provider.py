import pytest
from unittest.mock import Mock, patch
from sentra_rag.embeddings.provider import (
    EmbeddingProvider,
    SentenceTransformersProvider,
    get_embedding_provider
)


class TestEmbeddingProvider:
    
    def test_embedding_provider_is_abstract(self):
        """Test that EmbeddingProvider cannot be instantiated directly."""
        with pytest.raises(TypeError):
            EmbeddingProvider()

    @patch('sentra_rag.embeddings.provider.SentenceTransformer')
    def test_sentence_transformers_provider_init(self, mock_transformer):
        """Test SentenceTransformersProvider initialization."""
        mock_model = Mock()
        mock_transformer.return_value = mock_model
        
        provider = SentenceTransformersProvider("test-model")
        
        mock_transformer.assert_called_once_with("test-model")
        assert provider.model == mock_model

    @patch('sentra_rag.embeddings.provider.SentenceTransformer')
    def test_sentence_transformers_provider_embed_query(self, mock_transformer):
        """Test embedding generation."""
        mock_model = Mock()
        mock_model.encode.return_value.tolist.return_value = [0.1, 0.2, 0.3]
        mock_transformer.return_value = mock_model
        
        provider = SentenceTransformersProvider("test-model")
        result = provider.embed_query("test query")
        
        mock_model.encode.assert_called_once_with("test query")
        assert result == [0.1, 0.2, 0.3]

    @patch('sentra_rag.embeddings.provider.rag_settings')
    @patch('sentra_rag.embeddings.provider.SentenceTransformersProvider')
    def test_get_embedding_provider_singleton(self, mock_provider_class, mock_settings):
        """Test that get_embedding_provider returns a singleton."""
        mock_settings.embedding_model = "test-model"
        mock_provider = Mock()
        mock_provider_class.return_value = mock_provider
        
        # Clear any existing instance
        import sentra_rag.embeddings.provider
        sentra_rag.embeddings.provider._provider_instance = None
        
        # First call should create instance
        provider1 = get_embedding_provider()
        
        # Second call should return same instance
        provider2 = get_embedding_provider()
        
        assert provider1 == provider2
        mock_provider_class.assert_called_once_with(model_name="test-model")