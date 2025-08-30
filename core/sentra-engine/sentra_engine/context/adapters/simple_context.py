from typing import Optional
import uuid
from sentra_core.constants import SYSTEM_PROMPT
from sentra_engine.core.models import Message, PromptContext, RAGContext
from sentra_engine.context.ports.context import ContextPort
from sentra_engine.persistence.ports.persistence import PersistencePort
from sentra_engine.core.constants import CONTEXT_WINDOW_SIZE

class SimpleContextService(ContextPort):
    def __init__(self, persistence: PersistencePort, window_size: int = CONTEXT_WINDOW_SIZE):
        self.persistence = persistence
        self.window_size = window_size

    
    async def build(self, conversation_id: str, rag_context: Optional[RAGContext] = None) -> PromptContext:
        messages = list(await self.persistence.load_conversation(conversation_id) or [])
        
        # ⚠️ Prepend system message if missing
        system_message = Message(id=uuid.uuid4().hex, role="system", content=SYSTEM_PROMPT)
        full_context = [system_message] + messages[-self.window_size:]

        return PromptContext(messages=full_context)
