# tests/test_embeddings/test_provider.py
import pytest
from unittest.mock import Mock, patch
from sentra.rag.embeddings.base import EmbeddingProvider
from sentra.rag.embeddings.provider import get_embedding_provider
from sentra.rag.embeddings.sentence_transformers_provider import SentenceTransformersEmbeddingProvider


class TestEmbeddingProvider:
    def test_embedding_provider_is_abstract(self):
        """EmbeddingProvider cannot be instantiated directly."""
        with pytest.raises(TypeError):
            EmbeddingProvider()

    @patch("sentra.rag.embeddings.sentence_transformers_provider.SentenceTransformer")
    def test_sentence_transformers_provider_init(self, mock_transformer):
        """Ensure SentenceTransformer is initialized with model name."""
        mock_model = Mock()
        mock_transformer.return_value = mock_model

        provider = SentenceTransformersEmbeddingProvider("test-model")

        # Trigger lazy load
        _ = provider.model

        mock_transformer.assert_called_once_with("test-model")
        assert provider.model is mock_model

    @patch("sentra.rag.embeddings.sentence_transformers_provider.SentenceTransformer")
    def test_sentence_transformers_provider_embed_query(self, mock_transformer):
        """Ensure embed_query calls encode and unwraps result."""
        mock_model = Mock()
        fake_array = Mock()
        fake_array.tolist.return_value = [0.1, 0.2, 0.3]
        mock_model.encode.return_value = [fake_array]
        mock_transformer.return_value = mock_model

        provider = SentenceTransformersEmbeddingProvider("test-model")
        result = provider.embed_query("hello")

        mock_model.encode.assert_called_once_with(["hello"], normalize_embeddings=True)
        assert result == [0.1, 0.2, 0.3]


    @patch("sentra.rag.embeddings.provider.SentenceTransformersEmbeddingProvider")
    def test_get_embedding_provider_singleton(self, mock_provider_class):
        """get_embedding_provider should reuse the same instance."""
        mock_provider = Mock()
        mock_provider_class.return_value = mock_provider

        import sentra.rag.embeddings.provider as provider_module
        # Add caching at module level if missing
        if not hasattr(provider_module, "_provider_instance"):
            provider_module._provider_instance = None

        provider_module._provider_instance = None  # reset

        first = get_embedding_provider()
        second = get_embedding_provider()

        assert first is second
        mock_provider_class.assert_called_once()
