from __future__ import annotations
from typing import AsyncGenerator, Callable
from uuid import uuid4

from google.adk.events.event import Event
from google.genai import types

from sentra.runtime.agents.legal.use_case_contract_drafting import run_contract_drafting_agent
from sentra.runtime.agents.real_estate.use_case_listings_search import run_listings_search_agent
from sentra.runtime.context.builder import build_context, flatten_context
from sentra.runtime.errors import BudgetExhaustedError, TimeoutError, ToolError
from sentra.runtime.models import ConversationRequest
from sentra.runtime.orchestrators import route_legal_intent, route_real_estate_intent
from sentra.runtime.ports.event_sink import EventSink
from sentra.runtime.telemetry import emit_event_log
from sentra.runtime.runners.agent_runner import AgentRunner


# Routing table for specialized use-cases
SPECIAL_ROUTES: dict[str, Callable] = {
    "legal": run_contract_drafting_agent,
    "real_estate": run_listings_search_agent,
}


class CoordinatorAgent:
    """Routes conversation requests to the appropriate specialized agent or the general Sentra agent."""

    def __init__(self, sink: EventSink | None = None):
        self.sink = sink

    async def _persist(self, event: Event) -> None:
        if self.sink:
            await self.sink.on_event(event)

    async def run(self, request: ConversationRequest) -> AsyncGenerator[Event, None]:
        task_run_id = uuid4().hex
        msg = request.messages[-1]

        try:
            # 1. Explicit override (body.agent)
            selected = request.agent

            # 2. Intent routing if no override
            if not selected:
                if route_legal_intent(msg):
                    selected = "legal"
                elif route_real_estate_intent(msg):
                    selected = "real_estate"

            # 3. Dispatch specialized agent
            if selected in SPECIAL_ROUTES:
                async for ev in self._dispatch_special(selected, request, task_run_id):
                    yield ev
                return

            # 4. Fallback to Sentra agent
            async for ev in self._dispatch_sentra(request, task_run_id):
                yield ev

        except (ToolError, TimeoutError, BudgetExhaustedError):
            err_evt = Event(
                author="system",
                content=types.Content(role="system", parts=[types.Part(text="Coordinator agent failed")]),
                custom_metadata={"type": "error", "status": "error"},
            )
            yield err_evt
            raise


    async def _dispatch_special(
        self, name: str, request: ConversationRequest, task_run_id: str
    ) -> AsyncGenerator[Event, None]:
        emit_event_log(
            Event(
                author="system",
                content=types.Content(role="system", parts=[types.Part(text=f"Dispatching {name} agent")]),
                custom_metadata={"type": "step_start", "agent": name},
            )
        )

        context = await build_context(request)
        async for ev in SPECIAL_ROUTES[name](request, context, task_run_id):
            await self._persist(ev)
            yield ev

        yield Event(
            author="system",
            content=types.Content(role="system", parts=[types.Part(text=f"{name.capitalize()} agent completed")]),
            custom_metadata={"type": "step_end", "status": "success", "agent": name},
        )

    async def _dispatch_sentra(
        self, request: ConversationRequest, task_run_id: str
    ) -> AsyncGenerator[Event, None]:
        emit_event_log(
            Event(
                author="system",
                content=types.Content(role="system", parts=[types.Part(text="Dispatching Sentra agent")]),
                custom_metadata={"type": "step_start", "agent": "sentra"},
            )
        )

        context = await build_context(request)
        prompt = flatten_context(context, request.messages[-1])

        async for ev in AgentRunner.run("sentra_agent", prompt, request, self.sink):
            yield ev

        yield Event(
            author="system",
            content=types.Content(role="system", parts=[types.Part(text="Sentra agent completed")]),
            custom_metadata={"type": "step_end", "status": "success", "agent": "sentra"},
        )
