from __future__ import annotations

"""Coordinator agent orchestrating LLM calls.

This very small implementation streams a minimal set of events so that the
API layer can forward them as server-sent events.  When ``USE_DUMMY`` is set
in the environment the agent returns canned responses which are used by the
unit tests.  Otherwise a real LLM backend is queried based on the core
settings (either vLLM or llama-server).
"""

from typing import AsyncGenerator

import httpx

from sentra_core.settings import settings as core_settings, LLMEngine

from ..config import settings
from ..models import ConversationEvent, ConversationRequest


class CoordinatorAgent:
    """Minimal agent that delegates the request to an LLM service."""

    async def run(
        self, request: ConversationRequest
    ) -> AsyncGenerator[ConversationEvent, None]:
        """Stream conversation events produced by the coordinator.

        Args:
            request: Incoming conversation information.

        Yields:
            ConversationEvent objects representing the streaming response.
        """

        yield ConversationEvent(type="step_start", task_type="agent_execution")

        if settings.use_dummy:
            # Deterministic, fast path used for tests and demos
            yield ConversationEvent(
                type="message_delta", content="Hello from ADK engine"
            )
            yield ConversationEvent(type="message_final", content="Done.")
        else:
            text = await self._call_llm("\n".join(request.messages))
            yield ConversationEvent(type="message_delta", content=text)
            yield ConversationEvent(type="message_final", content=text)

        yield ConversationEvent(type="step_end", task_type="agent_execution")

    async def _call_llm(self, prompt: str) -> str:
        """Send the prompt to the configured LLM backend and return its text."""

        base_url: str
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

        # very tolerant parsing - different backends return different shapes
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
