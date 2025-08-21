from datetime import datetime, timezone
from typing import AsyncGenerator, Optional, Sequence
from sentra_engine.core.models import DeltaEvent, PromptContext, Message, ToolSchema
from sentra_engine.ports.context import ContextPort
from sentra_engine.ports.llm import LLMPort
from sentra_engine.core.models import Transcript, PlanStep
from sentra_engine.engine.id_utils import normalize_message_id
from sentra_engine.ports.persistence import PersistencePort
from dataclasses import is_dataclass, asdict
import inspect
from sentra_engine.ports.planner import PlannerPort
from sentra_engine.core.tool_orchestrator import ToolOrchestrator, normalize_tool_output
from sentra_engine.core.json_utils import parse_json_safe
import json  # Retained for json.dumps usage

class ConversationEngine:
    def __init__(
        self,
        *,
        context: ContextPort,
        llm: LLMPort,
        persistence: PersistencePort,
        planner: PlannerPort | None = None,
        tool_orchestrator: ToolOrchestrator | None = None,
    ):
        self.context = context
        self.llm = llm
        self.persistence = persistence
        self.planner = planner
        self.tool_orchestrator = tool_orchestrator

    async def _run_pipeline(
        self,
        *,
        user_id: str,
        conversation_id: str,
        message_id: Optional[str],
        response_message_id: Optional[str],
        content: str,
        use_planner: bool = False,
    ) -> AsyncGenerator[DeltaEvent, None]:
        """Common pipeline for handling conversation logic."""
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
        llm_messages = [*ctx_msgs, user_msg_openai]

        tools_schema: Optional[Sequence[ToolSchema]] = None
        if self.tool_orchestrator:
            try:
                tools_schema = await self.tool_orchestrator.registry()
            except Exception:
                tools_schema = None

        if use_planner and self.planner:
            transcript = Transcript(messages=[*(ctx.messages), user_msg])
            plan = await self.planner.plan(transcript=transcript, context="")
            guidance = (plan.params or {}).get("guidance") if plan else None
        else:
            guidance = None

        prelude_chunks: list[str] = []
        tool_requested = False
        tool_name: Optional[str] = None
        tool_args_buf: dict[int, list[str]] = {}

        async for ev in self.llm.chat_stream(PromptContext(messages=llm_messages), tools_schema=tools_schema, guidance=guidance):
            if ev.type == "message_delta" and ev.content:
                prelude_chunks.append(ev.content)
                yield ev
            elif ev.type == "tool_call_delta":
                tool_requested = True
                idx = int((ev.metadata or {}).get("index", 0))
                name = (ev.metadata or {}).get("name")
                if name:
                    tool_name = str(name)
                frag = (ev.metadata or {}).get("arguments_delta")
                if frag:
                    tool_args_buf.setdefault(idx, []).append(str(frag))
            elif ev.type == "tool_calls_done":
                break

        post_chunks: list[str] = []

        if tool_requested and self.tool_orchestrator and tool_name:
            args_json = "".join(tool_args_buf.get(0, [])) or "{}"
            try:
                args = parse_json_safe(args_json) or {}
            except Exception:
                args = {}
            step_id = normalize_message_id(None)
            result = await self.tool_orchestrator.execute_one(
                conversation_id=conversation_id,
                plan_step_id=step_id,
                tool_name=tool_name,
                args=args,
            )
            system_text = normalize_tool_output(tool_name, result.content if result.ok else result.error)
            system_msg = Message(
                id=normalize_message_id(None, prefer_hex=True),
                role="system",
                content=system_text,
                timestamp=datetime.now(timezone.utc).isoformat(),
            )
            await self.persistence.append_message(conversation_id, system_msg)
            llm_messages = [*llm_messages, _as_openai_msg(system_msg)]

            async for ev in self.llm.chat_stream(PromptContext(messages=llm_messages), guidance=guidance):
                if ev.type == "message_delta" and ev.content:
                    post_chunks.append(ev.content)
                    yield ev

        final_text = ("".join(prelude_chunks) + "".join(post_chunks)).strip() or "(no content)"
        assistant_msg = Message(
            id=normalize_message_id(response_message_id, prefer_hex=True),
            role="assistant",
            content=final_text,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        await self.persistence.append_message(conversation_id, assistant_msg)
        yield DeltaEvent(type="message_final", content="")

    async def run_fast(
        self,
        *,
        user_id: str,
        conversation_id: str,
        message_id: Optional[str],
        response_message_id: Optional[str],
        content: str,
    ) -> AsyncGenerator[DeltaEvent, None]:
        """Run the conversation engine in fast mode."""
        async for event in self._run_pipeline(
            user_id=user_id,
            conversation_id=conversation_id,
            message_id=message_id,
            response_message_id=response_message_id,
            content=content,
            use_planner=False,
        ):
            yield event

    async def run_planner(
        self,
        *,
        user_id: str,
        conversation_id: str,
        message_id: Optional[str],
        response_message_id: Optional[str],
        content: str,
    ) -> AsyncGenerator[DeltaEvent, None]:
        """Run the conversation engine with planner integration."""
        async for event in self._run_pipeline(
            user_id=user_id,
            conversation_id=conversation_id,
            message_id=message_id,
            response_message_id=response_message_id,
            content=content,
            use_planner=True,
        ):
            yield event
def _as_openai_msg(m: object) -> dict:
    try:
        if is_dataclass(m) and not inspect.isclass(m):
            d = asdict(m)
        elif isinstance(m, dict):
            d = m
        else:
            d = {"role": getattr(m, "role", None), "content": getattr(m, "content", None)}
        role = d["role"] if isinstance(d, dict) else None
        content = d["content"] if isinstance(d, dict) else None
        if role is None and content is None:
            return {"role": "system", "content": str(m)}
        return {"role": role or "system", "content": content or ""}
    except Exception:
        return {"role": "system", "content": str(m)}
