from __future__ import annotations

import time
from typing import AsyncGenerator
from uuid import uuid4

from google.adk.agents import Agent
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import Session
from google.genai import types

from google.adk.events.event import Event
from sentra.runtime.adapters.session_ephemeral import EphemeralSessionService
from sentra.runtime.context import build_context
from sentra.runtime.models import ConversationRequest
from sentra.runtime.policies.guardrails import check_tool_allowed
from sentra.runtime.telemetry import emit_event_log
from sentra.shared.settings import settings


class SentraAgent:
    """Agent that builds context and queries the LLM backend."""

    async def run(
        self, request: ConversationRequest, task_run_id: str
    ) -> AsyncGenerator[Event, None]:
        """Stream events produced by the agent."""

        # --- agent start
        start_evt = Event(author="system", content=types.Content(role="system", parts=[types.Part(text="Agent started")]), custom_metadata={"type": "agent_started"})
        emit_event_log(start_evt)
        yield Event(author="system", content=types.Content(role="system", parts=[types.Part(text="agent execution start")]), custom_metadata={"type": "step_start", "step": "agent_execution"})

        # --- build context
        if request.context_source_ids or request.context_document_ids:
            check_tool_allowed("SentraAgent", "RagTool")
        context = await build_context(request)
        emit_event_log(Event(author="system", content=types.Content(role="system", parts=[types.Part(text="Context built")]), custom_metadata={"type": "context_built"}))

        # --- assemble prompt
        prompt_parts: list[str] = []
        if context.get("memories"):
            prompt_parts.append(context["memories"])
        if context.get("history"):
            prompt_parts.append(context["history"])
        prompt_parts.append(request.messages[-1])
        prompt = "\n".join(prompt_parts)

        # --- ADK setup
        vllm = LiteLlm(model=settings.vllm_model, api_base=f"{settings.vllm_server_url}/v1")
        adk_agent = Agent(
            name="sentra_agent",
            model=vllm,
            instruction="You are a helpful assistant that uses context and tools.",
        )

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

        # --- stream loop
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
                        # delta = no constructor, must build directly
                        yield Event(author="assistant", content=types.Content(role="assistant", parts=[types.Part(text=part.text)]), custom_metadata={"type": "message_delta"})
            if ev.is_final_response():
                break

        # --- final message
        response = "".join(chunks)
        emit_event_log(Event(author="system", content=types.Content(role="system", parts=[types.Part(text="LLM called")]), custom_metadata={"type": "llm_called", "engine": settings.llm_engine.value}))
        yield Event(author="assistant", content=types.Content(role="assistant", parts=[types.Part(text=response)]), custom_metadata={"type": "message_final"})

        # --- agent completed
        emit_event_log(Event(author="system", content=types.Content(role="system", parts=[types.Part(text="Agent completed")]), custom_metadata={"type": "agent_completed", "status": "success"}))
        yield Event(author="system", content=types.Content(role="system", parts=[types.Part(text="agent execution end")]), custom_metadata={"type": "step_end", "step": "agent_execution"})
