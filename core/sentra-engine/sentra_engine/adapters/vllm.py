import httpx
from typing import AsyncGenerator, Optional, Sequence
from sentra_engine.core.models import PromptContext, DeltaEvent, ToolSchema
from sentra_engine.ports.llm import LLMPort
from ._openai_stream import (
    _strip_data_prefix,
    _parse_json_line,
    _extract_delta_content_from_obj,
    _extract_tool_call_deltas,
    _extract_finish_reason,
)

class VLLMAdapter(LLMPort):
    def __init__(self, base_url: str, *, model: str, request_timeout: float | None = None):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.request_timeout = request_timeout

    async def chat_stream(
        self,
        prompt_context: PromptContext,
        tools_schema: Optional[Sequence[ToolSchema]] = None,
        guidance: Optional[str] = None,
    ) -> AsyncGenerator[DeltaEvent, None]:
        url = f"{self.base_url}/v1/chat/completions"
        messages = prompt_context.messages
        if guidance:
            messages = [{"role": "system", "content": f"Planner guidance:\n{guidance}"}] + messages

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True,
        }

        if tools_schema:
            payload["tools"] = [
                {
                    "type": "function",
                    "function": {
                        "name": s.name,
                        "description": (s.description or s.title or s.name),  # NEW
                        "parameters": s.parameters,
                    },
                }
                for s in tools_schema
            ]
            payload["tool_choice"] = "auto"

        async with httpx.AsyncClient(timeout=self.request_timeout) as client:
            async with client.stream("POST", url, json=payload) as response:
                if response.status_code >= 400:
                    body = await response.aread()
                    raise RuntimeError(f"LLM error {response.status_code}: {body.decode(errors='replace')}")

                async for line in response.aiter_lines():
                    if not line or line.startswith(":"):
                        continue
                    stripped = _strip_data_prefix(line)
                    if stripped == "[DONE]":
                        break

                    obj = _parse_json_line(stripped)
                    if not obj:
                        continue

                    content = _extract_delta_content_from_obj(obj)
                    if content:
                        yield DeltaEvent(type="message_delta", content=content)

                    for tdelta in _extract_tool_call_deltas(obj):
                        yield DeltaEvent(type="tool_call_delta", metadata=tdelta)

                    fr = _extract_finish_reason(obj)
                    if fr == "tool_calls":
                        yield DeltaEvent(type="tool_calls_done")
