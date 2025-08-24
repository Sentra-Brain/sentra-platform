from typing import AsyncGenerator, Optional, Sequence
from sentra_engine.core.models import DeltaEvent, Message, ToolSchema, Transcript, StepEvent
from sentra_engine.core.time import utc_now_iso
from sentra_engine.core.id_utils import normalize_message_id
from sentra_engine.conversation.internal.step_runner import StepRunner
from sentra_engine.context.ports.context import ContextPort
from sentra_engine.llm.ports.llm import LLMPort
from sentra_engine.persistence.ports.persistence import PersistencePort
from sentra_engine.planner.ports.planner import PlannerPort
from sentra_engine.conversation.ports.rag import RAGPort
from sentra_engine.core.plan import Plan, Step
from sentra_engine.tools.ports.tool import ToolPort


class TurnRunner:
    def __init__(
        self,
        context: ContextPort,
        llm: LLMPort,
        persistence: PersistencePort,
        planner: Optional[PlannerPort] = None,
        tool_orchestrator: Optional[ToolPort] = None,
        rag: Optional[RAGPort] = None,
        max_rounds: int = 3,
        allow_plaintext_tool_fallback: bool = False,
    ) -> None:
        self.context = context
        self.llm = llm
        self.persistence = persistence
        self.planner = planner
        self.tool_orchestrator = tool_orchestrator
        self.rag = rag
        self.max_rounds = max_rounds
        self.allow_plaintext_tool_fallback = allow_plaintext_tool_fallback

    async def run_turn(
        self,
        conversation_id: str,
        message_id: Optional[str],
        response_message_id: Optional[str],
        content: str,
        use_planner: bool,
    ) -> AsyncGenerator[DeltaEvent, None]:
        user_msg = self._build_user_message(message_id, content)
        await self.persistence.append_message(conversation_id, user_msg)

        transcript = await self._build_transcript(conversation_id, user_msg)

        plan = await self._build_plan(transcript, use_planner)

        tools_schema = await self._resolve_tool_registry(conversation_id)

        async for ev in self._execute_plan(conversation_id, plan, transcript, tools_schema):
            yield ev

        final = await self._finalize_turn(conversation_id, response_message_id, transcript)
        yield DeltaEvent(type="message_final", content=final)

    def _build_user_message(self, message_id: Optional[str], content: str) -> Message:
        return Message(
            id=normalize_message_id(message_id, prefer_hex=True),
            role="user",
            content=content,
            timestamp=utc_now_iso(),
        )

    async def _build_transcript(self, conversation_id: str, user_msg: Message) -> list[Message]:
        ctx = await self.context.build(conversation_id)
        return [*ctx.messages, user_msg]

    async def _build_plan(self, transcript: list[Message], use_planner: bool) -> Plan:
        if use_planner and self.planner:
            try:
                return await self.planner.plan_structured(Transcript(messages=list(transcript)), context="")
            except Exception:
                return Plan(schema_version=1, steps=[Step(id="respond", kind="LLM.Respond")], entry="respond")
        return Plan(schema_version=1, steps=[Step(id="respond", kind="LLM.Respond")], entry="respond")

    async def _resolve_tool_registry(self, conversation_id: str) -> Optional[Sequence[ToolSchema]]:
        if self.tool_orchestrator:
            try:
                return await self.tool_orchestrator.registry()
            except Exception as e:
                await self._append_error_event(conversation_id, str(e))
        return None

    async def _append_error_event(self, conversation_id: str, error: str) -> None:
        try:
            await self.persistence.append_step_event(
                conversation_id,
                StepEvent(type="tools_unavailable", detail={"error": error})
            )
        except Exception:
            pass

    async def _execute_plan(
        self,
        conversation_id: str,
        plan: Plan,
        transcript: list[Message],
        tools_schema: Optional[Sequence[ToolSchema]],
    ) -> AsyncGenerator[DeltaEvent, None]:
        self._runner = StepRunner(
            conversation_id=conversation_id,
            llm=self.llm,
            persistence=self.persistence,
            tool_orchestrator=self.tool_orchestrator,
            rag=self.rag,
            tools_schema=tools_schema,
            max_rounds=self.max_rounds,
            allow_plaintext_fallback=self.allow_plaintext_tool_fallback,
        )
        async for ev in self._runner.run(plan, transcript):
            yield ev


    async def _finalize_turn(
        self, conversation_id: str, response_message_id: Optional[str], transcript: list[Message]
    ) -> str:
        final = self._runner.final_text or "(no content)"
        asst_msg = Message(
            id=normalize_message_id(response_message_id, prefer_hex=True),
            role="assistant",
            content=final,
            timestamp=utc_now_iso(),
        )
        await self.persistence.append_message(conversation_id, asst_msg)
        return final
