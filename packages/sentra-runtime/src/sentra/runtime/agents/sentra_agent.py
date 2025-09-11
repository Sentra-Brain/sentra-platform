from __future__ import annotations

from typing import AsyncGenerator
from uuid import uuid4

from google.adk.agents import Agent
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import Session
from google.genai import types

from sentra.domain.models.event import SentraEvent, SentraEventType
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
    ) -> AsyncGenerator[SentraEvent, None]:
        """Stream events produced by the agent."""

        # --- agent start
        # emit_event_log(SentraEvent.system_message("Agent started", task_run_id=task_run_id))
        yield SentraEvent(author="system", type=SentraEventType.STEP_START, task_run_id=task_run_id, meta={"step": "agent_execution"})

        # --- build context
        if request.context_source_ids or request.context_document_ids:
            check_tool_allowed("SentraAgent", "RagTool")
        context = await build_context(request)
        # emit_event_log(SentraEvent.system_message("Context built", task_run_id=task_run_id))

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
            session_id=conversation_id,
            state=state,
            events=[],
        )
        session_service = EphemeralSessionService(adk_session)
        run_config = RunConfig(streaming_mode=StreamingMode.SSE)

        runner = Runner(agent=adk_agent, app_name="sentra", session_service=session_service, session=adk_session)
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
                        yield SentraEvent(
                            author="assistant",
                            type=SentraEventType.MESSAGE_DELTA,
                            content={"role": "assistant", "parts": [{"text": part.text}]},
                            task_run_id=task_run_id,
                        )
            if ev.is_final_response():
                break

        # --- final message
        response = "".join(chunks)
        # emit_event_log(SentraEvent.system_message("LLM called", task_run_id=task_run_id, meta={"engine": settings.llm_engine.value}))
        yield SentraEvent.assistant_message(response, task_run_id=task_run_id)

        # --- agent completed
        # emit_event_log(SentraEvent.system_message("Agent completed", task_run_id=task_run_id, status="success"))
        yield SentraEvent(author="system", type=SentraEventType.STEP_END, task_run_id=task_run_id, meta={"step": "agent_execution"})
