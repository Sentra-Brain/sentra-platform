import httpx
import logging
from typing import List, Optional
from uuid import UUID

from sentra_engine.rag.ports.rag import RAGPort
from sentra_engine.rag.core.models.chunk import RagChunk

logger = logging.getLogger("rag")

class ChromaRAGAdapter(RAGPort):
    def __init__(self, base_url: str, timeout: int = 10):
        self.base_url = base_url
        self.timeout = timeout

    async def retrieve_chunks(
        self,
        query: str,
        source_ids: Optional[List[UUID]] = None,
        document_ids: Optional[List[UUID]] = None,
        limit: int = 5
    ) -> List[RagChunk]:
        payload = {
            "query": query,
            "source_ids": [str(sid) for sid in source_ids or []],
            "document_ids": [str(did) for did in document_ids or []],
            "limit": limit
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(f"{self.base_url}/search", json=payload)
                response.raise_for_status()
                data = response.json().get("results", [])
                return [RagChunk(**{
                    **item,
                    **item.get("metadata", {})
                }) for item in data]
        except Exception as e:
            logger.warning(f"[RAG] Retrieval failed: {e}")
            return []
