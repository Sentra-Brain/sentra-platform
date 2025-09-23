from __future__ import annotations
from typing import AsyncGenerator
import time
from uuid import uuid4

from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.runners import Runner
from google.adk.sessions import Session
from google.adk.events.event import Event
from google.genai import types

from sentra.runtime.adapters.session_ephemeral import EphemeralSessionService
from sentra.runtime.agents.agent_loader import AgentLoader
from sentra.runtime.ports.event_sink import EventSink


class AgentRunner:
    """Helper to run an ADK agent with consistent session setup and streaming."""

    @staticmethod
    async def run(
        agent_name: str,
        prompt: str,
        request,
        sink: EventSink | None = None,
    ) -> AsyncGenerator[Event, None]:
        loader = AgentLoader()
        adk_agent = loader.load_agent(agent_name)

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
                        delta_evt = Event(
                            author="assistant",
                            content=types.Content(role="assistant", parts=[types.Part(text=part.text)]),
                            custom_metadata={"type": "message_delta"},
                        )
                        if sink:
                            await sink.on_event(delta_evt)
                        yield delta_evt
            if ev.is_final_response():
                break

        final_text = "".join(chunks)
        final_evt = Event(
            author="assistant",
            content=types.Content(role="assistant", parts=[types.Part(text=final_text)]),
            custom_metadata={"type": "message_final"},
        )
        if sink:
            await sink.on_event(final_evt)
        yield final_evt
