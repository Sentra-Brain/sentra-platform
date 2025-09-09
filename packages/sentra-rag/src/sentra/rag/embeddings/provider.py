# packages/sentra-rag/src/sentra/rag/embeddings/provider.py
from typing import Optional
from sentra.rag.embeddings.base import EmbeddingProvider
from sentra.rag.embeddings.sentence_transformers_provider import SentenceTransformersEmbeddingProvider

_provider_instance: Optional[EmbeddingProvider] = None

def get_embedding_provider() -> EmbeddingProvider:
    global _provider_instance
    if _provider_instance is None:
        _provider_instance = SentenceTransformersEmbeddingProvider()
    return _provider_instance
