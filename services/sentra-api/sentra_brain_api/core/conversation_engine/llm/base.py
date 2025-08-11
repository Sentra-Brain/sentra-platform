from typing import AsyncIterator, Protocol, runtime_checkable, Dict, Any

@runtime_checkable
class LLMClient(Protocol):
    """Contrato mínimo para backends OpenAI‑like con streaming."""
    def chat_completion(self, payload: Dict[str, Any]) -> AsyncIterator[str]:
        """Itera líneas del stream (p.ej. 'data: {...}')."""
        ...

    async def healthcheck(self) -> bool:
        """True si el backend está vivo."""
        ...
