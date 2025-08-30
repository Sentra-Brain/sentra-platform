from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from sentra_engine.rag.core.models.chunk import RagChunk

class RAGPort(ABC):
    @abstractmethod
    async def retrieve_chunks(
        self,
        query: str,
        source_ids: Optional[List[UUID]] = None,
        document_ids: Optional[List[UUID]] = None,
        limit: int = 5
    ) -> List[RagChunk]:
        ...
