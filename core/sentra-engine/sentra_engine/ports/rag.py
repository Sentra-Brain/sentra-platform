# sentra_engine/ports/rag.py
from abc import ABC, abstractmethod
from typing import Optional
from sentra_engine.core.models import RAGContext


class RAGPort(ABC):
    @abstractmethod
    async def retrieve(
        self,
        query: str,
        filters: Optional[dict] = None,
    ) -> RAGContext:
        """Retrieve relevant context from RAG given a query and optional filters."""
        raise NotImplementedError
