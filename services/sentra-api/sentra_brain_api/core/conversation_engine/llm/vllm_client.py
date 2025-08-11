import httpx
from collections.abc import AsyncIterator
from typing import Any, Dict
from .base import LLMClient
from sentra_core.core.logging import get_logger
logger = get_logger(__name__)

class VLLMClient(LLMClient):
    def __init__(self, base_url: str, *, request_timeout: float | None = None):
        self.base_url = base_url.rstrip("/")
        self.request_timeout = request_timeout

    async def chat_completion(self, payload: Dict[str, Any]) -> AsyncIterator[str]:
        url = f"{self.base_url}/v1/chat/completions"
        async with httpx.AsyncClient(timeout=self.request_timeout) as client:
            async with client.stream("POST", url, json=payload) as response:
                if response.status_code >= 400:
                    body = await response.aread()
                    raise RuntimeError(
                        f"LLM error {response.status_code}: {body.decode(errors='replace')}"
                    )
                async for line in response.aiter_lines():
                    if line is not None:
                        yield line

    async def healthcheck(self) -> bool:
        url = f"{self.base_url}/v1/models"
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                logger.debug(f"Performing healthcheck on VLLM server at {url}")
                resp = await client.get(url)
                if resp.status_code != 200:
                    logger.error(f"VLLM server healthcheck failed: {resp.status_code}")
                return resp.status_code == 200
        except Exception:
            return False
