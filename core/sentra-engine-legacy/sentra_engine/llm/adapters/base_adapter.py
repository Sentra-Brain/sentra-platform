import httpx
from typing import AsyncGenerator, Optional, Sequence
from sentra_engine.core.models import PromptContext, DeltaEvent, ToolSchema
from sentra_engine.llm.ports.llm import LLMPort
from sentra_engine.core.json_utils import (
    parse_json_line,
    extract_delta_content,
    extract_tool_call_deltas,
    extract_finish_reason,
    strip_data_prefix,
)
from .openai_stream import with_guidance, apply_tools


class BaseLLMAdapter(LLMPort):
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
        messages = with_guidance(prompt_context.messages, guidance)

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True,
        }

        apply_tools(payload, tools_schema)

        async with httpx.AsyncClient(timeout=self.request_timeout) as client:
            async with client.stream("POST", url, json=payload) as response:
                if response.status_code >= 400:
                    body = await response.aread()
                    raise RuntimeError(f"LLM error {response.status_code}: {body.decode(errors='replace')}")

                async for line in response.aiter_lines():
                    if not line or line.startswith(":"):
                        continue
                    stripped = strip_data_prefix(line)
                    if stripped == "[DONE]":
                        break

                    obj = parse_json_line(stripped)
                    if not obj:
                        continue

                    content = extract_delta_content(obj)
                    if content:
                        yield DeltaEvent(type="message_delta", content=content)

                    for tdelta in extract_tool_call_deltas(obj):
                        yield DeltaEvent(type="tool_call_delta", metadata=tdelta)

                    fr = extract_finish_reason(obj)
                    if fr == "tool_calls":
                        yield DeltaEvent(type="tool_calls_done")
