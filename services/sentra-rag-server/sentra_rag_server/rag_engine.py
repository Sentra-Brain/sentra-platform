# /sentra-rag-server/sentra_rag_server/rag_engine.py
# Core RAG engine for processing queries and managing context
from sentra_rag.services.rag_service import RAGQueryService
from sentra_rag.core.settings import rag_settings


class RAGEngine:
    """Core RAG engine for processing queries and managing context."""
    
    def __init__(self):
        self.rag_service = RAGQueryService()
    
    async def search_knowledge(self, query: str, knowledge_source_id: str = None, limit: int = None):
        """Search for relevant knowledge chunks."""
        return await self.rag_service.search_documents(
            query=query,
            knowledge_source_id=knowledge_source_id,
            limit=limit
        )
    
    async def get_context(self, query: str, knowledge_source_id: str = None, max_tokens: int = None):
        """Get formatted context for LLM injection."""
        return await self.rag_service.get_context_for_query(
            query=query,
            knowledge_source_id=knowledge_source_id,
            max_tokens=max_tokens
        )
    
    def get_settings(self):
        """Get current RAG settings."""
        return {
            "chroma_url": rag_settings.chroma_url,
            "collection_name": rag_settings.collection_name,
            "embedding_model": rag_settings.embedding_model,
            "chunk_size": rag_settings.chunk_size,
            "max_context_tokens": rag_settings.max_context_tokens
        }