import httpx
from typing import AsyncGenerator, Optional, Sequence
from sentra_engine.core.models import PromptContext, DeltaEvent, ToolSchema
from sentra_engine.ports.llm import LLMPort
from ._openai_stream import _strip_data_prefix, _extract_delta_content

class LlamaServerAdapter(LLMPort):
    def __init__(self, base_url: str, *, model: str, request_timeout: float | None = None):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.request_timeout = request_timeout

    async def chat_stream(
        self,
        prompt_context: PromptContext,
        tools_schema: Optional[Sequence[ToolSchema]] = None,
        guidance: Optional[str] = None,
    ) -> AsyncGenerator[DeltaEvent, None]:  # Corrected return type
        url = f"{self.base_url}/v1/chat/completions"
        payload = {
            "model": self.model,
            "messages": prompt_context.messages,
            "stream": True,
        }

        async with httpx.AsyncClient(timeout=self.request_timeout) as client:
            async with client.stream("POST", url, json=payload) as response:
                if response.status_code >= 400:
                    body = await response.aread()
                    raise RuntimeError(f"LLM error {response.status_code}: {body.decode(errors='replace')}")

                async for line in response.aiter_lines():
                    if not line:
                        continue
                    if line.startswith(":"):
                        continue
                    stripped_line = _strip_data_prefix(line)
                    if stripped_line == "[DONE]":
                        break

                    content = _extract_delta_content(stripped_line)
                    if content:
                        yield DeltaEvent(type="message_delta", content=content)
