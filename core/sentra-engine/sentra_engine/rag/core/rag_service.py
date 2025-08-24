from sentra_engine.rag.ports.rag import RAGPort
from sentra_engine.rag.core.models.chunk import RagChunk
from typing import List, Optional
from uuid import UUID

class RagService:
    def __init__(self, rag_client: RAGPort):
        self.rag_client = rag_client

    async def retrieve_chunks(
        self,
        query: str,
        source_ids: Optional[List[UUID]] = None,
        document_ids: Optional[List[UUID]] = None,
        limit: int = 5
    ) -> List[RagChunk]:
        return await self.rag_client.retrieve_chunks(query, source_ids, document_ids, limit)
