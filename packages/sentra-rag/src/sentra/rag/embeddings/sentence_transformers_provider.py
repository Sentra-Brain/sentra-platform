# packages/sentra-rag/src/sentra/rag/embeddings/sentence_transformers_provider.py
from typing import List
from sentence_transformers import SentenceTransformer
from sentra.rag.embeddings.base import EmbeddingProvider
from sentra.rag.settings import rag_settings
from sentra.shared.logging import get_logger

logger = get_logger(__name__)


class SentenceTransformersEmbeddingProvider(EmbeddingProvider):
    """Embedding provider using a local SentenceTransformer model."""

    def __init__(self, model_name: str = None):
        self.model_name = model_name or rag_settings.embedding_model
        self._model = None
    @property
    def model(self) -> SentenceTransformer:
        if self._model is None:
            logger.info(f"Loading sentence-transformer model: {self.model_name}")
            self._model = SentenceTransformer(self.model_name)
            logger.info("Embedding model loaded")
        return self._model

    def embed_query(self, text: str) -> List[float]:
        logger.info("Generating embedding for query")
        return self.model.encode([text], normalize_embeddings=True)[0].tolist()

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        logger.info(f"Generating embeddings for {len(texts)} documents")
        return self.model.encode(texts, normalize_embeddings=True).tolist()
