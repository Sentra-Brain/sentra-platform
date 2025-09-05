from __future__ import annotations

from typing import AsyncGenerator

from uuid import uuid4

from google.adk.models.lite_llm import LiteLlm
from google.adk.agents import Agent
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.runners import Runner
from google.adk.sessions import BaseSessionService
from google.genai import types

from sentra.domain.services import session_service
from sentra.shared.settings import settings as core_settings
from sentra.shared.services import RagMemoryService
from google.adk.sessions import Session
from .. import config
from ..context import build_context
from ..models import EngineEvent, ConversationRequest
from ..telemetry import emit_event_log
from sentra.runtime.policies.guardrails import check_tool_allowed
from sentra.runtime.adapters.mongo_session_service import MongoSessionService


class SentraAgent:
    """Agent that builds context and queries the LLM backend."""

    async def run(
        self, request: ConversationRequest
    ) -> AsyncGenerator[EngineEvent, None]:
        """Stream events produced by the agent."""
        task_run_id = uuid4().hex
        emit_event_log(EngineEvent(type="agent_started", task_run_id=task_run_id))

        yield EngineEvent(
            type="step_start", task_type="agent_execution", task_run_id=task_run_id
        )

        memory_service = RagMemoryService()

        if request.context_source_ids or request.context_document_ids:
            check_tool_allowed("SentraAgent", "RagTool")
        context = await build_context(request)
        emit_event_log(EngineEvent(type="context_built", task_run_id=task_run_id))
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
        user_id = request.user_id or "user"
        conversation_id = request.conversation_id or uuid4().hex
        session_service: BaseSessionService = MongoSessionService()
        session = await session_service.get_session(
            app_name="sentra", user_id=user_id, session_id=conversation_id
        )
        if session is None:
            raise RuntimeError(
                f"Session not found for user_id={user_id}, session_id={conversation_id}. "
                "Session must exist in both MongoDB and SQL."
            )
        # Convert SessionEntity to dict, then to ADK Session
        adk_session = Session.model_validate(session.model_dump())
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
                        yield EngineEvent(
                            type="message_delta",
                            content=part.text,
                            task_run_id=task_run_id,
                        )
            if ev.is_final_response():
                break
        response = "".join(chunks)
        emit_event_log(
            EngineEvent(
                type="llm_called",
                task_run_id=task_run_id,
                meta={"engine": core_settings.llm_engine.value},
            )
        )
        yield EngineEvent(
            type="message_final", content=response, task_run_id=task_run_id
        )

        await memory_service.add_session_to_memory(session)

        emit_event_log(
            EngineEvent(
                type="agent_completed", task_run_id=task_run_id, status="success"
            )
        )
        yield EngineEvent(
            type="step_end", task_type="agent_execution", task_run_id=task_run_id
        )
