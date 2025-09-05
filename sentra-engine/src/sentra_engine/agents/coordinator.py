from __future__ import annotations

"""Coordinator agent that delegates to the general SentraAgent."""

from typing import AsyncGenerator

from ..context import build_context
from ..errors import BudgetExhaustedError, TimeoutError, ToolError
from ..models import EngineEvent, ConversationRequest
from ..telemetry import emit_event_log
from .sentra_agent import SentraAgent
from ..orchestrators import route_legal_intent, route_real_estate_intent
from .legal.use_case_contract_drafting import run_contract_drafting_agent
from .real_estate.use_case_listings_search import run_listings_search_agent
from ..adapters.persistence_adapter import SessionPersistenceAdapter


class CoordinatorAgent:
    """Thin wrapper that forwards requests to :class:`SentraAgent`.

    The agent attempts to route the request to more specialised agents and
    falls back to a simplified flow if tools fail, time out or budgets are
    exhausted.
    """

    def __init__(self, persistence: SessionPersistenceAdapter | None = None):
        self.persistence = persistence

    async def _persist(self, event: EngineEvent) -> None:
        if self.persistence:
            await self.persistence.persist_event(event)

    async def run(
        self, request: ConversationRequest, fallback: bool = False
    ) -> AsyncGenerator[EngineEvent, None]:
        try:
            if fallback:
                # Fallback mode: no tools or planners, short context
                event = EngineEvent(type="step_start", task_type="fallback")
                await self._persist(event)
                yield event
                event = EngineEvent(
                    type="message_delta",
                    content="I'm here to help, but cannot access external tools right now.",
                )
                await self._persist(event)
                yield event
                event = EngineEvent(type="step_end", task_type="fallback")
                await self._persist(event)
                yield event
                return

            msg = request.messages[-1]

            if route_legal_intent(msg):
                emit_event_log(
                    EngineEvent(type="agent_dispatched", label="legal")
                )
                context = await build_context(request)
                async for event in run_contract_drafting_agent(request, context):
                    await self._persist(event)
                    yield event
                return

            if route_real_estate_intent(msg):
                emit_event_log(
                    EngineEvent(type="agent_dispatched", label="real_estate")
                )
                context = await build_context(request)
                async for event in run_listings_search_agent(request, context):
                    await self._persist(event)
                    yield event
                return

            emit_event_log(EngineEvent(type="fallback_triggered"))
            agent = SentraAgent()
            async for event in agent.run(request):
                await self._persist(event)
                yield event

        except (ToolError, TimeoutError, BudgetExhaustedError):
            if fallback:
                raise
            async for event in self.run(request, fallback=True):
                await self._persist(event)
                yield event
