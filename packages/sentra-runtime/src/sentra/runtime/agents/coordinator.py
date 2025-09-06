from __future__ import annotations

"""Coordinator agent that delegates to the general SentraAgent."""

from typing import AsyncGenerator

from sentra.runtime.agents.legal.use_case_contract_drafting import run_contract_drafting_agent
from sentra.runtime.agents.real_estate.use_case_listings_search import run_listings_search_agent
from sentra.runtime.agents.sentra_agent import SentraAgent
from sentra.runtime.context import build_context
from sentra.runtime.errors import BudgetExhaustedError, TimeoutError, ToolError
from sentra.runtime.models import EngineEvent, ConversationRequest
from sentra.runtime.orchestrators import route_legal_intent, route_real_estate_intent
from sentra.runtime.ports.event_sink import EventSink
from sentra.runtime.telemetry import emit_event_log


class CoordinatorAgent:
    """Thin wrapper that forwards requests to :class:`SentraAgent`.

    The agent attempts to route the request to more specialised agents and
    falls back to a simplified flow if tools fail, time out or budgets are
    exhausted.
    """

    def __init__(self, sink: EventSink | None = None):
        self.sink = sink

    async def _persist(self, event: EngineEvent) -> None:
        if self.sink:
            await self.sink.on_event(event)

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
                emit_event_log(EngineEvent(type="agent_dispatched", label="legal"))
                context = await build_context(request)
                async for event in run_contract_drafting_agent(request, context):
                    await self._persist(event)
                    yield event
                return

            if route_real_estate_intent(msg):
                emit_event_log(EngineEvent(type="agent_dispatched", label="real_estate"))
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
