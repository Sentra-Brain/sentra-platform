from __future__ import annotations

from typing import AsyncGenerator

from uuid import uuid4

from google.adk.models.lite_llm import LiteLlm
from google.adk.agents import Agent
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.runners import Runner
from google.genai import types

from sentra.shared.settings import settings as core_settings
from sentra.runtime.context import build_context
from sentra.runtime.models import ConversationRequest
from sentra.runtime.telemetry import emit_event_log
from sentra.schemas import Event
from sentra.runtime.policies.guardrails import check_tool_allowed


class SentraAgent:
    """Agent that builds context and queries the LLM backend."""

    async def run(
        self, request: ConversationRequest
    ) -> AsyncGenerator[Event, None]:
        """Stream events produced by the agent."""
        task_run_id = uuid4().hex
        emit_event_log(Event(type="agent_started", role="system", task_run_id=task_run_id))

        yield Event(
            type="step_start",
            role="system",
            task_type="agent_execution",
            task_run_id=task_run_id,
        )

        if request.context_source_ids or request.context_document_ids:
            check_tool_allowed("SentraAgent", "RagTool")
        context = await build_context(request)
        emit_event_log(Event(type="context_built", role="system", task_run_id=task_run_id))
        prompt_parts = []
        if context.get("memories"):
            prompt_parts.append(context["memories"])
        if context.get("history"):
            prompt_parts.append(context["history"])
        prompt_parts.append(request.messages[-1])
        prompt = "\n".join(prompt_parts)

        vllm = LiteLlm(
            model=core_settings.vllm_model,
            api_base=f"{core_settings.vllm_server_url}/v1",
        )
        adk_agent = Agent(
            name="sentra_agent",
            model=vllm,
            instruction="You are a helpful assistant that uses context and tools.",
        )
        from sentra.runtime.adapters.session_ephemeral import EphemeralSessionService
        from google.adk.sessions import Session

        user_id = request.user_id or "user"
        conversation_id = request.conversation_id or uuid4().hex
        state = request.session_state or {"session": {}, "user": {}, "app": {}}
        adk_session = Session(
            app_name="sentra",
            user_id=user_id,
            session_id=conversation_id,
            state=state,
            events=[],
        )
        session_service = EphemeralSessionService(adk_session)
        run_config = RunConfig(streaming_mode=StreamingMode.SSE)
        runner = Runner(
            agent=adk_agent,
            app_name="sentra",
            session_service=session_service,
            session=adk_session,
        )
        content = types.Content(role="user", parts=[types.Part(text=prompt)])
        chunks: list[str] = []
        async for ev in runner.run_async(
            user_id=user_id,
            session_id=conversation_id,
            new_message=content,
            run_config=run_config
        ):
            if ev.content and ev.content.parts:
                for part in ev.content.parts:
                    if part.text:
                        chunks.append(part.text)
                        yield Event(
                            type="message_delta",
                            role="assistant",
                            content=part.text,
                            task_run_id=task_run_id,
                        )
            if ev.is_final_response():
                break
        response = "".join(chunks)
        emit_event_log(
            Event(
                type="llm_called",
                role="system",
                task_run_id=task_run_id,
                meta={"engine": core_settings.llm_engine.value},
            )
        )
        yield Event(
            type="message_final",
            role="assistant",
            content=response,
            task_run_id=task_run_id,
        )

        emit_event_log(
            Event(
                type="agent_completed",
                role="system",
                task_run_id=task_run_id,
                status="success",
            )
        )
        yield Event(
            type="step_end",
            role="system",
            task_type="agent_execution",
            task_run_id=task_run_id,
        )
