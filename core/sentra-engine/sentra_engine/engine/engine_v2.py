from dataclasses import dataclass
from typing import AsyncGenerator, Optional, Sequence

from sentra_engine.core.models import DeltaEvent, Message, PromptContext, ToolSchema, Transcript
from sentra_engine.core.time import utc_now_iso
from sentra_engine.engine.id_utils import normalize_message_id
from sentra_engine.ports.context import ContextPort
from sentra_engine.ports.llm import LLMPort
from sentra_engine.ports.persistence import PersistencePort
from sentra_engine.ports.planner import PlannerPort
from sentra_engine.ports.rag import RAGPort
from sentra_engine.core.tool_orchestrator import ToolOrchestrator
from sentra_engine.tooling.parser import ToolStreamParser
from sentra_engine.tooling.formatters import normalize_tool_output


@dataclass
class EngineConfig:
    max_rounds: int = 3
    allow_plaintext_tool_fallback: bool = False


class ConversationEngineV2:
    """Small, boring turn runner. Tool parsing & execution delegated to tooling/ + orchestrator."""

    def __init__(
        self,
        *,
        context: ContextPort,
        llm: LLMPort,
        persistence: PersistencePort,
        planner: Optional[PlannerPort] = None,
        tool_orchestrator: Optional[ToolOrchestrator] = None,
        rag: Optional[RAGPort] = None,
        config: EngineConfig = EngineConfig(),
    ) -> None:
        self.context = context
        self.llm = llm
        self.persistence = persistence
        self.planner = planner
        self.tool_orchestrator = tool_orchestrator
        self.rag = rag
        self.config = config

    async def run_fast(
        self,
        *,
        user_id: str,
        conversation_id: str,
        message_id: Optional[str],
        response_message_id: Optional[str],
        content: str,
    ) -> AsyncGenerator[DeltaEvent, None]:
        async for ev in self._run_turn(conversation_id, message_id, response_message_id, content, use_planner=False):
            yield ev

    async def run_planner(
        self,
        *,
        user_id: str,
        conversation_id: str,
        message_id: Optional[str],
        response_message_id: Optional[str],
        content: str,
    ) -> AsyncGenerator[DeltaEvent, None]:
        async for ev in self._run_turn(conversation_id, message_id, response_message_id, content, use_planner=True):
            yield ev

    async def _run_turn(
        self,
        conversation_id: str,
        message_id: Optional[str],
        response_message_id: Optional[str],
        content: str,
        *,
        use_planner: bool,
    ) -> AsyncGenerator[DeltaEvent, None]:
        # 1) append user message
        user_msg = Message(
            id=normalize_message_id(message_id, prefer_hex=True),
            role="user",
            content=content,
            timestamp=utc_now_iso(),
        )
        await self.persistence.append_message(conversation_id, user_msg)

        # 2) build transcript
        ctx = await self.context.build(conversation_id)
        transcript: list[Message] = [*ctx.messages, user_msg]

        # 3) optional planner (guidance only for now)
        guidance: Optional[str] = None
        if use_planner and self.planner:
            try:
                plan = await self.planner.plan(Transcript(messages=list(transcript)), context="")
                guidance = (plan.params or {}).get("guidance")
            except Exception:
                guidance = None

        # 4) loop: LLM -> tool intents? -> execute -> append system msgs -> repeat
        text_acc: list[str] = []
        for _ in range(self.config.max_rounds):
            tools_schema: Optional[Sequence[ToolSchema]] = None
            if self.tool_orchestrator:
                try:
                    tools_schema = await self.tool_orchestrator.registry()
                except Exception:
                    tools_schema = None
                    # (optional) append a tools_unavailable step event here

            parser = ToolStreamParser(allow_plaintext_fallback=self.config.allow_plaintext_tool_fallback)
            agen = self.llm.chat_stream(
                PromptContext(messages=[_as_openai_msg(m) for m in transcript]),
                tools_schema=tools_schema,
                guidance=guidance,
            )
            try:
                async for ev in agen:
                    if ev.type == "message_delta" and ev.content:
                        text_acc.append(ev.content)
                        yield DeltaEvent(type="message_delta", content=ev.content)
                    parser.ingest(ev)
            finally:
                if hasattr(agen, "aclose"):
                    await agen.aclose()

            intents = parser.finalize_intents()
            if not intents or not self.tool_orchestrator:
                break

            # Execute tool calls and append system messages
            for call in intents:
                res = await self.tool_orchestrator.execute_one(
                    conversation_id=conversation_id,
                    plan_step_id=normalize_message_id(None),
                    tool_name=call.name,
                    args=call.arguments,
                    tool_call_id=call.id,
                )
                system_msg = Message(
                    id=normalize_message_id(None, prefer_hex=True),
                    role="system",
                    content=normalize_tool_output(call.name, res.content if res.ok else res.error),
                    timestamp=utc_now_iso(),
                )
                await self.persistence.append_message(conversation_id, system_msg)
                transcript.append(system_msg)

            # use guidance once unless planner says otherwise
            guidance = None

        final = ("".join(text_acc)).strip() or "(no content)"
        asst_msg = Message(
            id=normalize_message_id(response_message_id, prefer_hex=True),
            role="assistant",
            content=final,
            timestamp=utc_now_iso(),
        )
        await self.persistence.append_message(conversation_id, asst_msg)
        yield DeltaEvent(type="message_final", content=final)


def _as_openai_msg(m: Message) -> dict:
    return {"role": (m.role or "system"), "content": (m.content or "")}
