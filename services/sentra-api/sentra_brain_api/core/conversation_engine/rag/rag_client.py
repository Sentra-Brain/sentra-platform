# sentra_brain_api/core/conversation_engine/rag_client.py

import httpx
from typing import List, Optional
from sentra_brain_api.core.conversation_engine.rag.rag_chunk import RagChunk
from sentra_brain_api.core.conversation_engine.rag.rag_client_setings import settings 
import logging

logger = logging.getLogger("rag_client")

class RagClient:
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or settings.rag_server_url
        self.timeout = settings.query_timeout

    async def retrieve_relevant_chunks(
        self,
        query: str,
        source_ids: Optional[List[str]] = None,
        document_ids: Optional[List[str]] = None,
        limit: int = 5
    ) -> List[RagChunk]:
        payload = {
            "query": query,
            "source_ids": source_ids or [],
            "document_ids": document_ids or [],
            "limit": limit
        }

        url = f"{self.base_url}/search"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                results = data.get("results", [])
                chunks: list[RagChunk] = []

                for item in results:
                    try:
                        chunk = RagChunk(
                            chunk_id=item["chunk_id"],
                            content=item["content"],
                            relevance_score=item.get("relevance_score", 0.0),
                            document_id=item["metadata"]["document_id"],
                            knowledge_source_id=item["metadata"]["knowledge_source_id"],
                            source_type=item["metadata"].get("source_type", "unknown"),
                            filename=item["metadata"].get("filename"),
                            chunk_index=item["metadata"].get("chunk_index"),
                            chunk_length=item["metadata"].get("chunk_length"),
                        )
                        chunks.append(chunk)
                    except Exception as e:
                        logger.warning(f"Invalid RAG chunk skipped: {e}")
                return chunks
        except Exception as e:
            logger.error(f"[RAG] Failed to retrieve context: {e}")
            return []
