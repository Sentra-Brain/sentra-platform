from dataclasses import dataclass
from typing import AsyncGenerator, Optional, Sequence

from sentra_engine.core.models import DeltaEvent, Message, ToolSchema, Transcript
from sentra_engine.core.plan import Plan, Step
from sentra_engine.core.time import utc_now_iso
from sentra_engine.engine.id_utils import normalize_message_id
from sentra_engine.engine.step_runner import StepRunner
from sentra_engine.ports.context import ContextPort
from sentra_engine.ports.llm import LLMPort
from sentra_engine.ports.persistence import PersistencePort
from sentra_engine.ports.planner import PlannerPort
from sentra_engine.ports.rag import RAGPort
from sentra_engine.core.tool_orchestrator import ToolOrchestrator
from sentra_engine.core.models import StepEvent


@dataclass
class EngineConfig:
    max_rounds: int = 3
    allow_plaintext_tool_fallback: bool = False


class ConversationEngine:
    """Conversation Engine for managing user interactions. It handles message processing,
     context management, and tool orchestration."""

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

        # 3) planner -> structured plan (or synthesize a single Respond)
        plan: Plan
        if use_planner and self.planner:
            try:
                plan = await self.planner.plan_structured(Transcript(messages=list(transcript)), context="")
            except Exception:
                # fallback: single Respond
                plan = Plan(schema_version=1, steps=[Step(id="respond", kind="LLM.Respond")], entry="respond")
        else:
            plan = Plan(schema_version=1, steps=[Step(id="respond", kind="LLM.Respond")], entry="respond")

        # 4) resolve tool registry ONCE (with visible event on failure)
        tools_schema: Optional[Sequence[ToolSchema]] = None
        if self.tool_orchestrator:
            try:
                tools_schema = await self.tool_orchestrator.registry()
            except Exception as e:
                tools_schema = None
                try:
                    await self.persistence.append_step_event(
                        conversation_id,
                        StepEvent(type="tools_unavailable", detail={"error": str(e)})
                    )
                except Exception:
                    pass  # best-effort

        # 5) run the plan
        runner = StepRunner(
            conversation_id=conversation_id,
            llm=self.llm,
            persistence=self.persistence,
            tool_orchestrator=self.tool_orchestrator,
            rag=self.rag,
            tools_schema=tools_schema,
            max_rounds=self.config.max_rounds,
            allow_plaintext_fallback=self.config.allow_plaintext_tool_fallback,
        )

        async for ev in runner.run(plan, transcript):
            # stream deltas to caller
            yield ev

        final = runner.final_text
        asst_msg = Message(
            id=normalize_message_id(response_message_id, prefer_hex=True),
            role="assistant",
            content=final,
            timestamp=utc_now_iso(),
        )
        await self.persistence.append_message(conversation_id, asst_msg)
        yield DeltaEvent(type="message_final", content=final)
