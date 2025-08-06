import httpx
from typing import AsyncGenerator

class VLLMClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def chat_completion(self, payload: dict) -> AsyncGenerator[str, None]:
        url = f"{self.base_url}/v1/chat/completions"
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream("POST", url, json=payload) as response:
                if response.status_code >= 400:
                    body = await response.aread()
                    raise RuntimeError(f"LLM error {response.status_code}: {body.decode(errors='replace')}")
                async for line in response.aiter_lines():
                    yield line

    async def healthcheck(self) -> bool:
        url = f"{self.base_url}/v1/models"
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(url)
                return response.status_code == 200
        except Exception as e:
            return False