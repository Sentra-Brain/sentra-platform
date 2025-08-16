from datetime import datetime, timezone
from typing import AsyncGenerator, Optional
from sentra_engine.core.models import DeltaEvent, PromptContext, Message
from sentra_engine.ports.context import ContextPort
from sentra_engine.ports.llm import LLMPort
from sentra_engine.engine.id_utils import normalize_message_id
from sentra_engine.ports.persistence import PersistencePort

class ConversationEngine:
    def __init__(
        self,
        *,
        context: ContextPort,
        llm: LLMPort,
        persistence: PersistencePort,
    ):
        self.context = context
        self.llm = llm
        self.persistence = persistence

    async def run_fast(
        self,
        *,
        user_id: str,
        conversation_id: str,
        message_id: Optional[str],
        response_message_id: Optional[str],
        content: str,
    ) -> AsyncGenerator[DeltaEvent, None]:
        now = datetime.now(timezone.utc).isoformat()

        user_msg = Message(
            id=normalize_message_id(message_id, prefer_hex=True),
            role="user",
            content=content,
            timestamp=now,
        )
        await self.persistence.append_message(conversation_id, user_msg)

        ctx = await self.context.build(conversation_id)
        prompt_ctx = PromptContext(messages=[*ctx.messages, user_msg])

        buffer = []
        async for ev in self.llm.chat_stream(prompt_ctx):
            if ev.type == "message_delta" and ev.content:
                buffer.append(ev.content)
                yield ev

        final_text = "".join(buffer).strip() or "(no content)"

        assistant_msg = Message(
            id=normalize_message_id(response_message_id, prefer_hex=True),
            role="assistant",
            content=final_text,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        await self.persistence.append_message(conversation_id, assistant_msg)

        yield DeltaEvent(type="message_final", content="")
