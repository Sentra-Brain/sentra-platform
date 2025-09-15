from __future__ import annotations

from typing import AsyncGenerator
from uuid import uuid4

from google.adk.events.event import Event
from google.genai import types
from sentra.runtime.agents.legal.use_case_contract_drafting import run_contract_drafting_agent
from sentra.runtime.agents.real_estate.use_case_listings_search import run_listings_search_agent
from sentra.runtime.agents.agent_loader import AgentLoader
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
        loader = AgentLoader()

        try:
            # Explicit override short-circuit (if provided)
            if getattr(request, "agent", None):
                selected = request.agent
                emit_event_log(Event(author="system", content=types.Content(role="system", parts=[types.Part(text=f"Dispatching overridden agent: {selected}")]), custom_metadata={"type": "step_start", "agent": selected}))
                # If override matches specialised intents, fall through to existing flows
                if selected in {"legal", "real_estate"}:
                    msg_override = msg  # reuse message for intent-specific flows
                    # force route by pretending the intent matched
                    if selected == "legal":
                        context = await build_context(request)
                        async for event in run_contract_drafting_agent(request, context, task_run_id):
                            await self._persist(event)
                            yield event
                        yield Event(author="system", content=types.Content(role="system", parts=[types.Part(text="Legal agent completed")]), custom_metadata={"type": "step_end", "status": "success", "agent": "legal"})
                        return
                    if selected == "real_estate":
                        context = await build_context(request)
                        async for event in run_listings_search_agent(request, context, task_run_id):
                            await self._persist(event)
                            yield event
                        yield Event(author="system", content=types.Content(role="system", parts=[types.Part(text="Real estate agent completed")]), custom_metadata={"type": "step_end", "status": "success", "agent": "real_estate"})
                        return
                # Otherwise default to dynamic loading path below by skipping intent checks.
                # Setting msg to empty string prevents accidental routing.
                msg = ""  # type: ignore
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

            # --- Default to dynamically loaded general agent ---
            emit_event_log(Event(author="system", content=types.Content(role="system", parts=[types.Part(text="Dispatching default_agent")]), custom_metadata={"type": "step_start", "agent": "default_agent"}))

            # Build context for default agent (mirroring previous SentraAgent behaviour)
            context = await build_context(request)
            prompt_parts: list[str] = []
            if context.get("memories"):
                prompt_parts.append(context["memories"])
            if context.get("history"):
                prompt_parts.append(context["history"])
            prompt_parts.append(request.messages[-1])
            prompt = "\n".join(prompt_parts)

            adk_agent = loader.load_agent("default_agent")

            # Use ADK runner directly (simplified variant of SentraAgent.run)
            from google.adk.agents.run_config import RunConfig, StreamingMode  # local import to reduce cold start
            from google.adk.runners import Runner
            from google.adk.sessions import Session
            from sentra.runtime.adapters.session_ephemeral import EphemeralSessionService
            import time

            user_id = request.user_id or "user"
            conversation_id = request.conversation_id or uuid4().hex
            state = request.session_state or {"session": {}, "user": {}, "app": {}}

            adk_session = Session(
                app_name="sentra",
                user_id=user_id,
                id=conversation_id,
                state=state,
                events=[],
                last_update_time=time.time(),
            )
            session_service = EphemeralSessionService(adk_session)
            run_config = RunConfig(streaming_mode=StreamingMode.SSE)
            runner = Runner(agent=adk_agent, app_name="sentra", session_service=session_service)
            content = types.Content(role="user", parts=[types.Part(text=prompt)])

            chunks: list[str] = []
            async for ev in runner.run_async(
                user_id=user_id,
                session_id=conversation_id,
                new_message=content,
                run_config=run_config,
            ):
                if ev.content and ev.content.parts:
                    for part in ev.content.parts:
                        if part.text:
                            chunks.append(part.text)
                            delta_evt = Event(author="assistant", content=types.Content(role="assistant", parts=[types.Part(text=part.text)]), custom_metadata={"type": "message_delta"})
                            await self._persist(delta_evt)
                            yield delta_evt
                if ev.is_final_response():
                    break

            final_text = "".join(chunks)
            final_evt = Event(author="assistant", content=types.Content(role="assistant", parts=[types.Part(text=final_text)]), custom_metadata={"type": "message_final"})
            await self._persist(final_evt)
            yield final_evt
            end_evt = Event(author="system", content=types.Content(role="system", parts=[types.Part(text="default_agent completed")]), custom_metadata={"type": "step_end", "status": "success", "agent": "default_agent"})
            await self._persist(end_evt)
            yield end_evt

        except (ToolError, TimeoutError, BudgetExhaustedError):
            yield Event(author="system", content=types.Content(role="system", parts=[types.Part(text="Coordinator agent failed")]), custom_metadata={"type": "error", "status": "error"})
            raise
