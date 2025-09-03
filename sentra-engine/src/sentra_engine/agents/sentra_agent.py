from __future__ import annotations

from typing import AsyncGenerator

from uuid import uuid4

from google.adk.models.lite_llm import LiteLlm
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.genai import types

from sentra_core.settings import settings as core_settings

from .. import config
from ..context import build_context
from ..models import ConversationEvent, ConversationRequest
from ..telemetry import emit_event_log
from sentra_engine.policies.guardrails import check_tool_allowed
from ..adapters.mongo_session_service import MongoSessionService


class SentraAgent:
    """Agent that builds context and queries the LLM backend."""

    async def run(
        self, request: ConversationRequest
    ) -> AsyncGenerator[ConversationEvent, None]:
        """Stream events produced by the agent."""
        task_run_id = uuid4().hex
        emit_event_log(ConversationEvent(type="agent_started", task_run_id=task_run_id))
        yield ConversationEvent(
            type="step_start", task_type="agent_execution", task_run_id=task_run_id
        )

        if request.context_source_ids or request.context_document_ids:
            check_tool_allowed("SentraAgent", "RagTool")
        context = await build_context(request)
        emit_event_log(ConversationEvent(type="context_built", task_run_id=task_run_id))
        prompt = f"{context.get('history', '')}\n{request.messages[-1]}"

        if config.settings.use_dummy:
            emit_event_log(
                ConversationEvent(
                    type="llm_called",
                    task_run_id=task_run_id,
                    meta={"engine": "dummy"},
                )
            )
            # Deterministic, fast path used for tests and demos
            yield ConversationEvent(
                type="message_delta",
                content="Hello from ADK engine",
                task_run_id=task_run_id,
            )
            yield ConversationEvent(
                type="message_final", content="Done.", task_run_id=task_run_id
            )
        else:
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
            from sentra_core.infra.nosql.mongo_conversation_repository import (
                get_conversation_mongo_repository,
            )
            session_service = MongoSessionService(
                repo=get_conversation_mongo_repository(),
                user_id=user_id,
                conversation_id=conversation_id,
            )
            await session_service.create_session(
                app_name="sentra", user_id=user_id, session_id=conversation_id
            )
            runner = Runner(
                agent=adk_agent,
                app_name="sentra",
                session_service=session_service,
            )
            content = types.Content(role="user", parts=[types.Part(text=prompt)])
            chunks: list[str] = []
            async for ev in runner.run_async(
                user_id=user_id,
                session_id=conversation_id,
                new_message=content,
            ):
                if ev.content and ev.content.parts:
                    for part in ev.content.parts:
                        if part.text:
                            chunks.append(part.text)
                            yield ConversationEvent(
                                type="message_delta",
                                content=part.text,
                                task_run_id=task_run_id,
                            )
                if ev.is_final_response():
                    break
            response = "".join(chunks)
            emit_event_log(
                ConversationEvent(
                    type="llm_called",
                    task_run_id=task_run_id,
                    meta={"engine": core_settings.llm_engine.value},
                )
            )
            yield ConversationEvent(
                type="message_final", content=response, task_run_id=task_run_id
            )

        emit_event_log(
            ConversationEvent(
                type="agent_completed", task_run_id=task_run_id, status="success"
            )
        )
        yield ConversationEvent(
            type="step_end", task_type="agent_execution", task_run_id=task_run_id
        )
