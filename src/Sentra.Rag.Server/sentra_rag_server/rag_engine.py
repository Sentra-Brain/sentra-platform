# /Sentra.Rag.Server/sentra_rag_server/rag_engine.py
# Core RAG engine for processing queries and managing context
from sentra.rag.services.rag_service import RAGQueryService
from sentra.rag.settings import rag_settings
from sentra.rag.embeddings.provider import get_embedding_provider
import chromadb
from asyncio import to_thread
from datetime import datetime
from uuid import uuid4


class RAGEngine:
    """Core RAG engine for processing queries and managing context."""
    
    def __init__(self):
        self.rag_service = RAGQueryService()
        # Setup embedding provider and dedicated memories collection
        self.embedding_provider = get_embedding_provider()
        chroma_host = rag_settings.chroma_url.replace("http://", "").replace("https://", "")
        host, port = chroma_host.split(":") if ":" in chroma_host else (chroma_host, "8000")
        self._memory_client = chromadb.HttpClient(host=host, port=int(port))
        self._memories = self._memory_client.get_or_create_collection(name="memories")
    
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

    async def memorize(self, user_id: str, session_id: str, text: str) -> str:
        """Store a piece of text in the user-scoped memories collection."""

        memory_id = uuid4().hex
        embedding = self.embedding_provider.embed_query(text)
        metadata = {
            "user_id": user_id,
            "session_id": session_id,
            "created_at": datetime.utcnow().isoformat(),
        }

        def _add() -> None:
            self._memories.add(
                ids=[memory_id],
                embeddings=[embedding],
                documents=[text],
                metadatas=[metadata],
            )

        await to_thread(_add)
        return memory_id

    async def search_memories(self, user_id: str, query: str, limit: int) -> list[dict]:
        """Search user memories filtered by ``user_id``."""

        embedding = self.embedding_provider.embed_query(query)

        def _query() -> list[dict]:
            result = self._memories.query(
                query_embeddings=[embedding],
                n_results=limit,
                where={"user_id": user_id},
            )
            return [
                {
                    "id": result["ids"][0][i],
                    "document": result["documents"][0][i],
                    "metadata": result["metadatas"][0][i],
                    "distance": result["distances"][0][i],
                }
                for i in range(len(result["ids"][0]))
            ]

        return await to_thread(_query)
