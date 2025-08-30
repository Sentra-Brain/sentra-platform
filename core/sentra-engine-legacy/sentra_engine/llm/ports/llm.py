# sentra_engine/ports/llm.py
from abc import ABC, abstractmethod
from typing import AsyncGenerator, AsyncIterator, Optional, Sequence
from sentra_engine.core.models import PromptContext, ToolSchema, DeltaEvent


class LLMPort(ABC):
    @abstractmethod
    def chat_stream(
        self,
        prompt_context: PromptContext,
        tools_schema: Optional[Sequence[ToolSchema]] = None,
        guidance: Optional[str] = None,
    ) -> AsyncIterator[DeltaEvent]:
        """Stream LLM response deltas given prompt context and optional tool schemas."""
        raise NotImplementedError
