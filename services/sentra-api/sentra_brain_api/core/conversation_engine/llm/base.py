from typing import AsyncIterator, Protocol, runtime_checkable, Dict, Any

@runtime_checkable
class LLMClient(Protocol):
    """Minimum contract for OpenAI-like backends with streaming."""
    def chat_completion(self, payload: Dict[str, Any]) -> AsyncIterator[str]:
        """Iterate over lines of the stream (e.g., 'data: {...}')."""
        ...

    async def healthcheck(self) -> bool:
        """True if the backend is alive."""
        ...
