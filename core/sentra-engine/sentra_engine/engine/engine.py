from datetime import datetime, timezone
from typing import AsyncGenerator, Optional
from sentra_engine.core.models import DeltaEvent, PromptContext, Message
from sentra_engine.ports.context import ContextPort
from sentra_engine.ports.llm import LLMPort
from sentra_engine.core.models import Transcript, PlanStep
from sentra_engine.engine.id_utils import normalize_message_id
from sentra_engine.ports.persistence import PersistencePort
from dataclasses import is_dataclass, asdict
import inspect

from sentra_engine.ports.planner import PlannerPort

class ConversationEngine:
    def __init__(
        self,
        *,
        context: ContextPort,
        llm: LLMPort,
        persistence: PersistencePort,
        planner: PlannerPort | None = None
    ):
        self.context = context
        self.llm = llm
        self.persistence = persistence
        self.planner = planner

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
        ctx_msgs = [_as_openai_msg(m) for m in ctx.messages]
        user_msg_openai = _as_openai_msg(user_msg)
        prompt_ctx = PromptContext(messages=[*ctx_msgs, user_msg_openai])
        
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

    async def run_planner(
        self, *, user_id: str, conversation_id: str,
        message_id: Optional[str], response_message_id: Optional[str], content: str
    ):
        now = datetime.now(timezone.utc).isoformat()
        user_msg = Message(id=normalize_message_id(message_id, prefer_hex=True),
                           role="user", content=content, timestamp=now)
        await self.persistence.append_message(conversation_id, user_msg)

        ctx = await self.context.build(conversation_id)
        ctx_msgs = [_as_openai_msg(m) for m in ctx.messages]
        user_msg_openai = _as_openai_msg(user_msg)

        # plan
        transcript = Transcript(messages=[*(ctx.messages), user_msg])
        if not self.planner:
            plan = PlanStep(action="Respond", params={"guidance": ""})
        else:
            plan = await self.planner.plan(transcript=transcript, context="")

        guidance = (plan.params or {}).get("guidance") if plan else None
        prompt_ctx = PromptContext(messages=[*ctx_msgs, user_msg_openai])

        buffer: list[str] = []
        async for ev in self.llm.chat_stream(prompt_ctx, guidance=guidance):
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

def _as_openai_msg(m: object) -> dict:
    try:
        if is_dataclass(m) and not inspect.isclass(m):
            d = asdict(m)
        elif isinstance(m, dict):
            d = m
        else:
            # generic fallback
            d = {"role": getattr(m, "role", None), "content": getattr(m, "content", None)}
        role = d["role"] if isinstance(d, dict) else None
        content = d["content"] if isinstance(d, dict) else None
        if role is None and content is None:
            return {"role": "system", "content": str(m)}
        return {"role": role or "system", "content": content or ""}
    except Exception:
        # last resort
        return {"role": "system", "content": str(m)}
