from dataclasses import dataclass
from typing import AsyncGenerator, Optional, Sequence

from sentra_engine.core.models import DeltaEvent, Message, ToolSchema, Transcript
from sentra_engine.core.plan import Plan, Step
from sentra_engine.core.time import utc_now_iso
from sentra_engine.engine.id_utils import normalize_message_id
from sentra_engine.engine.step_runner import StepRunner
from sentra_engine.engine.turn_runner import TurnRunner
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
        self.turn_runner = TurnRunner(
            context=context,
            llm=llm,
            persistence=persistence,
            planner=planner,
            tool_orchestrator=tool_orchestrator,
            rag=rag,
            max_rounds=config.max_rounds,
            allow_plaintext_tool_fallback=config.allow_plaintext_tool_fallback,
        )

    async def run_fast(
        self,
        *,
        user_id: str,
        conversation_id: str,
        message_id: Optional[str],
        response_message_id: Optional[str],
        content: str,
    ) -> AsyncGenerator[DeltaEvent, None]:
        async for ev in self.turn_runner.run_turn(
            conversation_id=conversation_id,
            message_id=message_id,
            response_message_id=response_message_id,
            content=content,
            use_planner=False,
        ):
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
        async for ev in self.turn_runner.run_turn(
            conversation_id=conversation_id,
            message_id=message_id,
            response_message_id=response_message_id,
            content=content,
            use_planner=True,
        ):
            yield ev
