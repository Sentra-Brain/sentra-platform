from typing import Optional
from sentra_engine.core.models import PromptContext, RAGContext
from sentra_engine.context.ports.context import ContextPort
from sentra_engine.persistence.ports.persistence import PersistencePort
from sentra_engine.core.constants import CONTEXT_WINDOW_SIZE

class SimpleContextService(ContextPort):
    def __init__(self, persistence: PersistencePort, window_size: int = CONTEXT_WINDOW_SIZE):
        self.persistence = persistence
        self.window_size = window_size

    async def build(self, conversation_id: str, rag_context: Optional[RAGContext] = None) -> PromptContext:
        messages = await self.persistence.load_conversation(conversation_id) or []
        trimmed = messages[-self.window_size:]
        return PromptContext(messages=trimmed)
