from sentra_rag.settings import rag_settings
from sentra_rag.vector_store.base import BaseVectorStore
from sentra_rag.vector_store.chroma_http import ChromaHttpVectorStore
from sentra_rag.vector_store.chroma_sdk import ChromaSdkVectorStore


def get_vector_store_service() -> BaseVectorStore:
    mode = rag_settings.vector_store_mode  # "http" or "sdk"
    if mode == "http":
        return ChromaHttpVectorStore()
    elif mode == "sdk":
        return ChromaSdkVectorStore()
    else:
        raise ValueError(f"Unknown vector store mode: {mode}")
