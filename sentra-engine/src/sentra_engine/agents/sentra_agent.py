from __future__ import annotations

from typing import AsyncGenerator

import httpx
from uuid import uuid4

from sentra_core.settings import LLMEngine, settings as core_settings

from .. import config
from ..context import build_context
from ..models import ConversationEvent, ConversationRequest
from ..telemetry import emit_event_log
from sentra_engine.policies.guardrails import check_tool_allowed


class SentraAgent:
    """Agent that builds context and queries the LLM backend."""

    async def run(
        self, request: ConversationRequest
    ) -> AsyncGenerator[ConversationEvent, None]:
        """Stream events produced by the agent."""
        task_run_id = uuid4().hex
        emit_event_log(
            ConversationEvent(type="agent_started", task_run_id=task_run_id)
        )
        yield ConversationEvent(
            type="step_start", task_type="agent_execution", task_run_id=task_run_id
        )

        if request.context_source_ids or request.context_document_ids:
            check_tool_allowed("SentraAgent", "RagTool")
        context = await build_context(request)
        emit_event_log(
            ConversationEvent(type="context_built", task_run_id=task_run_id)
        )
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
            response = await self._call_llm(prompt)
            emit_event_log(
                ConversationEvent(
                    type="llm_called",
                    task_run_id=task_run_id,
                    meta={"engine": core_settings.llm_engine.value},
                )
            )
            yield ConversationEvent(
                type="message_delta", content=response, task_run_id=task_run_id
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

    async def _call_llm(self, prompt: str) -> str:
        """Send the prompt to the configured LLM backend and return its text."""

        if core_settings.llm_engine == LLMEngine.LLAMA:
            base_url = f"{core_settings.llama_server_url}/completion"
            payload = {"prompt": prompt}
        else:  # default to vLLM style API
            base_url = f"{core_settings.vllm_server_url}/generate"
            payload = {"prompt": prompt}

        try:
            async with httpx.AsyncClient(
                timeout=core_settings.llm_request_timeout
            ) as client:
                resp = await client.post(base_url, json=payload)
                resp.raise_for_status()
                data = resp.json()
        except Exception as exc:  # pragma: no cover - network errors
            return f"LLM error: {exc}"

        if isinstance(data, dict):
            if "text" in data:
                txt = data["text"]
                if isinstance(txt, list):
                    return "".join(txt)
                return str(txt)
            if "content" in data:
                return str(data["content"])
            if "generated_text" in data:
                return str(data["generated_text"])
        return str(data)
