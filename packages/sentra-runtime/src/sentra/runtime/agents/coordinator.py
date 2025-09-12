from __future__ import annotations

from typing import AsyncGenerator
from uuid import uuid4

from google.adk.events.event import Event
from google.genai import types
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

    async def _persist(self, event: Event) -> None:
        if self.sink:
            await self.sink.on_event(event)

    async def run(self, request: ConversationRequest) -> AsyncGenerator[Event, None]:
        task_run_id = uuid4().hex
        msg = request.messages[-1]

        try:
            # --- Legal intent ---
            if route_legal_intent(msg):
                event = Event(author="system", content=types.Content(role="system", parts=[types.Part(text="Dispatching legal agent")]), custom_metadata={"type": "step_start", "agent": "legal"})
                emit_event_log(event)
                await self._persist(event)

                context = await build_context(request)
                async for event in run_contract_drafting_agent(request, context, task_run_id):                    
                    await self._persist(event)
                    yield event

                yield Event(author="system", content=types.Content(role="system", parts=[types.Part(text="Legal agent completed")]), custom_metadata={"type": "step_end", "status": "success", "agent": "legal"})
                return

            # --- Real estate intent ---
            if route_real_estate_intent(msg):
                event = Event(author="system", content=types.Content(role="system", parts=[types.Part(text="Dispatching real estate agent")]), custom_metadata={"type": "step_start", "agent": "real_estate"})
                emit_event_log(event)
                await self._persist(event)

                context = await build_context(request)
                async for event in run_listings_search_agent(request, context, task_run_id):
                    await self._persist(event)
                    yield event

                yield Event(author="system", content=types.Content(role="system", parts=[types.Part(text="Real estate agent completed")]), custom_metadata={"type": "step_end", "status": "success", "agent": "real_estate"})
                return

            # --- Default to general SentraAgent ---
            emit_event_log(Event(author="system", content=types.Content(role="system", parts=[types.Part(text="Dispatching general agent")]), custom_metadata={"type": "step_start", "agent": "sentra"}))
            agent = SentraAgent()
            async for event in agent.run(request, task_run_id=task_run_id):
                await self._persist(event)
                yield event

            yield Event(author="system", content=types.Content(role="system", parts=[types.Part(text="General agent completed")]), custom_metadata={"type": "step_end", "status": "success", "agent": "sentra"})

        except (ToolError, TimeoutError, BudgetExhaustedError):
            yield Event(author="system", content=types.Content(role="system", parts=[types.Part(text="Coordinator agent failed")]), custom_metadata={"type": "error", "status": "error"})
            raise
