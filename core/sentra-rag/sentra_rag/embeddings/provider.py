# sentra_rag/embeddings/service.py

from sentra_rag.embeddings.base import EmbeddingProvider
from sentra_rag.embeddings.sentence_transformers_provider import SentenceTransformersEmbeddingProvider


def get_embedding_provider() -> EmbeddingProvider:
    # For now, we only support SentenceTransformers
    # This allows for easy extension if we add more providers later
    return SentenceTransformersEmbeddingProvider()
