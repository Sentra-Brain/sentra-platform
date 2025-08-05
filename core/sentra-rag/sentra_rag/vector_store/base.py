from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from uuid import UUID


class BaseVectorStore(ABC):
    @abstractmethod
    async def query_similar_chunks(
        self, query_embedding: List[float], knowledge_source_id: Optional[UUID], limit: int
    ) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def index_document_chunks(
        self,
        document_id: UUID,
        knowledge_source_id: UUID,
        chunks: List[str],
        embeddings: List[List[float]],
        filename: str,
        source_type: str = "file"
    ) -> int:
        pass

    @abstractmethod
    async def delete_document_chunks(self, document_id: UUID) -> int:
        pass
