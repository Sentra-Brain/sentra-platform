
import httpx
from sentra_brain_api.core.config import settings

class LlamaServerClient:
    def __init__(self, base_url: str = None):
          self.base_url = base_url or settings.llama_server_url

    async def chat_completion(self, payload: dict) -> httpx.Response:
        url = f"{self.base_url}/v1/chat/completions"
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            return response
