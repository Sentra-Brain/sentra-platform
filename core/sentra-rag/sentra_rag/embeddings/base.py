# sentra_rag/embeddings/base.py

from abc import ABC, abstractmethod
from typing import List


class EmbeddingProvider(ABC):
    """Interface for embedding providers."""

    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        """Embed a single query string."""
        pass

    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple documents."""
        pass
