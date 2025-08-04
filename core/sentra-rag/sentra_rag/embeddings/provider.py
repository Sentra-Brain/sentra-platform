from typing import List
from abc import ABC, abstractmethod

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

from sentra_rag.core.settings import rag_settings


class EmbeddingProvider(ABC):
    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        pass


class SentenceTransformersProvider(EmbeddingProvider):
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise RuntimeError("sentence-transformers not available. Install with: pip install 'sentra-rag[ml]'")
        self.model = SentenceTransformer(model_name)

    def embed_query(self, text: str) -> List[float]:
        return self.model.encode(text).tolist()


_provider_instance: EmbeddingProvider | None = None


def get_embedding_provider() -> EmbeddingProvider:
    global _provider_instance
    if _provider_instance is None:
        model_name = rag_settings.embedding_model or "all-MiniLM-L6-v2"
        _provider_instance = SentenceTransformersProvider(model_name=model_name)
    return _provider_instance