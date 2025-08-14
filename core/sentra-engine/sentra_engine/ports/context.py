# sentra_engine/ports/context.py
from abc import ABC, abstractmethod
from typing import Optional
from sentra_engine.core.models import PromptContext, RAGContext


class ContextPort(ABC):
    @abstractmethod
    async def build(
        self,
        conversation_id: str,
        rag_context: Optional[RAGContext] = None,
    ) -> PromptContext:
        """Build a prompt context from conversation history and optional RAG context."""
        raise NotImplementedError
