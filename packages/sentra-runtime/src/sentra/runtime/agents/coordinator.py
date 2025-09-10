from __future__ import annotations

from typing import AsyncGenerator
from uuid import uuid4

from sentra.domain.models.event import SentraEvent, SentraEventType
from sentra.runtime.agents.legal.use_case_contract_drafting import run_contract_drafting_agent
from sentra.runtime.agents.real_estate.use_case_listings_search import run_listings_search_agent
from sentra.runtime.agents.sentra_agent import SentraAgent
from sentra.runtime.context import build_context
from sentra.runtime.errors import BudgetExhaustedError, TimeoutError, ToolError
from sentra.runtime.models import ConversationRequest
from sentra.runtime.orchestrators import route_legal_intent, route_real_estate_intent
from sentra.runtime.ports.event_sink import EventSink
from sentra.runtime.telemetry import emit_event_log


class CoordinatorAgent:
    """Delegates a conversation request to a specialised agent or the general SentraAgent."""

    def __init__(self, sink: EventSink | None = None):
        self.sink = sink

    async def _persist(self, event: SentraEvent) -> None:
        if self.sink:
            await self.sink.on_event(event)

    async def run(self, request: ConversationRequest) -> AsyncGenerator[SentraEvent, None]:
        task_run_id = uuid4().hex
        msg = request.messages[-1]

        try:
            # --- Legal intent ---
            if route_legal_intent(msg):
                event = SentraEvent.system_message("Dispatching legal agent", type=SentraEventType.STEP_START, task_run_id=task_run_id, meta={"agent": "legal"})
                emit_event_log(event)
                await self._persist(event)

                context = await build_context(request)
                async for event in run_contract_drafting_agent(request, context, task_run_id):                    
                    await self._persist(event)
                    yield event

                yield SentraEvent.system_message("Legal agent completed", type=SentraEventType.STEP_END, task_run_id=task_run_id, status="success", meta={"agent": "legal"})
                return

            # --- Real estate intent ---
            if route_real_estate_intent(msg):
                event = SentraEvent.system_message("Dispatching real estate agent", type=SentraEventType.STEP_START,     task_run_id=task_run_id, meta={"agent": "real_estate"})
                emit_event_log(event)
                await self._persist(event)

                context = await build_context(request)
                async for event in run_listings_search_agent(request, context, task_run_id):
                    await self._persist(event)
                    yield event

                yield SentraEvent.system_message("Real estate agent completed", type=SentraEventType.STEP_END, task_run_id=task_run_id, status="success", meta={"agent": "real_estate"})
                return

            # --- Default to general SentraAgent ---
            emit_event_log(SentraEvent.system_message("Dispatching general agent", type=SentraEventType.STEP_START, task_run_id=task_run_id, meta={"agent": "sentra"}))
            agent = SentraAgent()
            async for event in agent.run(request, task_run_id=task_run_id):
                await self._persist(event)
                yield event

            yield SentraEvent.system_message("General agent completed", type=SentraEventType.STEP_END, task_run_id=task_run_id, status="success", meta={"agent": "sentra"})

        except (ToolError, TimeoutError, BudgetExhaustedError):
            yield SentraEvent.error("Coordinator agent failed", task_run_id=task_run_id)
            raise
