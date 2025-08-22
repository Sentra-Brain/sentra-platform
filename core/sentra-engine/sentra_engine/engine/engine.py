from datetime import datetime, timezone
from typing import AsyncGenerator, Optional, Sequence

from dataclasses import asdict, is_dataclass
import inspect

from sentra_engine.core.json_utils import parse_json_safe
from sentra_engine.core.models import (
    DeltaEvent,
    Message,
    PromptContext,
    ToolSchema,
    Transcript,
)
from sentra_engine.core.tool_orchestrator import (
    ToolOrchestrator,
    normalize_tool_output,
)
from sentra_engine.engine.id_utils import normalize_message_id
from sentra_engine.ports.context import ContextPort
from sentra_engine.ports.llm import LLMPort
from sentra_engine.ports.persistence import PersistencePort
from sentra_engine.ports.planner import PlannerPort
from sentra_engine.ports.rag import RAGPort

class ConversationEngine:
    def __init__(
        self,
        *,
        context: ContextPort,
        llm: LLMPort,
        persistence: PersistencePort,
        planner: PlannerPort | None = None,
        tool_orchestrator: ToolOrchestrator | None = None,
        rag: RAGPort | None = None,
    ):
        self.context = context
        self.llm = llm
        self.persistence = persistence
        self.planner = planner
        self.tool_orchestrator = tool_orchestrator
        self.rag = rag

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
        transcript_msgs: list[Message] = [*ctx.messages, user_msg]
        llm_messages = [_as_openai_msg(m) for m in transcript_msgs]

        tools_schema: Optional[Sequence[ToolSchema]] = None
        if self.tool_orchestrator:
            try:
                tools_schema = await self.tool_orchestrator.registry()
            except Exception:
                tools_schema = None

        chunks: list[str] = []

        async def _call_llm(
            *,
            allow_tools: bool,
            guidance: Optional[str] = None,
        ) -> tuple[list[str], list[dict]]:
            prelude: list[str] = []
            calls: dict[int, dict] = {}
            async for ev in self.llm.chat_stream(
                PromptContext(messages=llm_messages),
                tools_schema=tools_schema if allow_tools else None,
                guidance=guidance,
            ):
                if ev.type == "message_delta" and ev.content:
                    prelude.append(ev.content)
                elif ev.type == "tool_call_delta":
                    idx = int((ev.metadata or {}).get("index", 0))
                    name = (ev.metadata or {}).get("name")
                    if name:
                        calls.setdefault(idx, {})["name"] = str(name)
                    frag = (ev.metadata or {}).get("arguments_delta")
                    if frag:
                        calls.setdefault(idx, {}).setdefault("args", []).append(str(frag))
                elif ev.type == "tool_calls_done":
                    break
            ordered = []
            for idx in sorted(calls.keys()):
                name = calls[idx].get("name")
                args_json = "".join(calls[idx].get("args", [])) or "{}"
                try:
                    args = parse_json_safe(args_json) or {}
                except Exception:
                    args = {}
                if name:
                    ordered.append({"name": name, "args": args})
            return prelude, ordered

        if use_planner and self.planner:
            while True:
                plan = await self.planner.plan(Transcript(messages=list(transcript_msgs)), context="")
                action = (plan.action or "Respond") if plan else "Respond"
                params = plan.params if plan else {}
                if action in {"Respond", "AskParams"}:
                    pre, _ = await _call_llm(allow_tools=False, guidance=params.get("guidance"))
                    for c in pre:
                        yield DeltaEvent(type="message_delta", content=c)
                    chunks.extend(pre)
                    break
                if action == "RetrieveRAG" and self.rag:
                    query = params.get("query") or content
                    filters = params.get("filters")
                    rag_ctx = await self.rag.retrieve(query, filters)
                    system_text = normalize_tool_output("rag", rag_ctx)
                    system_msg = Message(
                        id=normalize_message_id(None, prefer_hex=True),
                        role="system",
                        content=system_text,
                        timestamp=datetime.now(timezone.utc).isoformat(),
                    )
                    await self.persistence.append_message(conversation_id, system_msg)
                    transcript_msgs.append(system_msg)
                    llm_messages.append(_as_openai_msg(system_msg))
                    continue
                if action == "CallTool" and self.tool_orchestrator:
                    pre, calls = await _call_llm(allow_tools=True, guidance=params.get("guidance"))
                    for c in pre:
                        yield DeltaEvent(type="message_delta", content=c)
                    chunks.extend(pre)
                    for call in calls:
                        step_id = normalize_message_id(None)
                        result = await self.tool_orchestrator.execute_one(
                            conversation_id=conversation_id,
                            plan_step_id=step_id,
                            tool_name=call["name"],
                            args=call["args"],
                        )
                        system_text = normalize_tool_output(
                            call["name"],
                            result.content if result.ok else result.error,
                        )
                        system_msg = Message(
                            id=normalize_message_id(None, prefer_hex=True),
                            role="system",
                            content=system_text,
                            timestamp=datetime.now(timezone.utc).isoformat(),
                        )
                        await self.persistence.append_message(conversation_id, system_msg)
                        transcript_msgs.append(system_msg)
                        llm_messages.append(_as_openai_msg(system_msg))
                    continue
                # Fallback: respond immediately
                pre, _ = await _call_llm(allow_tools=False, guidance=params.get("guidance"))
                for c in pre:
                    yield DeltaEvent(type="message_delta", content=c)
                chunks.extend(pre)
                break
        else:
            while True:
                pre, calls = await _call_llm(allow_tools=True)
                for c in pre:
                    yield DeltaEvent(type="message_delta", content=c)
                chunks.extend(pre)
                if not calls or not self.tool_orchestrator:
                    break
                for call in calls:
                    step_id = normalize_message_id(None)
                    result = await self.tool_orchestrator.execute_one(
                        conversation_id=conversation_id,
                        plan_step_id=step_id,
                        tool_name=call["name"],
                        args=call["args"],
                    )
                    system_text = normalize_tool_output(
                        call["name"],
                        result.content if result.ok else result.error,
                    )
                    system_msg = Message(
                        id=normalize_message_id(None, prefer_hex=True),
                        role="system",
                        content=system_text,
                        timestamp=datetime.now(timezone.utc).isoformat(),
                    )
                    await self.persistence.append_message(conversation_id, system_msg)
                    transcript_msgs.append(system_msg)
                    llm_messages.append(_as_openai_msg(system_msg))
                continue

        final_text = ("".join(chunks)).strip() or "(no content)"
        assistant_msg = Message(
            id=normalize_message_id(response_message_id, prefer_hex=True),
            role="assistant",
            content=final_text,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        await self.persistence.append_message(conversation_id, assistant_msg)
        yield DeltaEvent(type="message_final", content=final_text)

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
