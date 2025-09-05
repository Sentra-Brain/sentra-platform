from __future__ import annotations

"""Implementation of :class:`MemoryService` backed by sentra-rag-server."""

from typing import List

import httpx

from sentra.domain.session_entity import SessionEntity
from sentra.shared.logging import get_logger
from sentra.shared.settings import settings

from .memory_service import MemoryService


logger = get_logger(__name__)


class RagMemoryService(MemoryService):
    """Memory service delegating persistence and search to ``rag-server``."""

    def __init__(self) -> None:
        self.base_url = settings.rag_server_url.rstrip("/")

    async def add_session_to_memory(self, session: SessionEntity) -> None:
        """Send the latest assistant messages from ``session`` to rag-server."""

        if not session.events:
            return

        url = f"{self.base_url}/memorize"
        async with httpx.AsyncClient() as client:
            for event in session.events:
                author = getattr(event, "author", None) or (event.meta or {}).get("author")
                if event.type == "message_final" and author in (None, "assistant"):
                    text = event.content if isinstance(event.content, str) else str(event.content)
                    payload = {
                        "user_id": session.user_id,
                        "session_id": session.session_id,
                        "text": text,
                    }
                    try:
                        await client.post(url, json=payload, timeout=10.0)
                    except Exception as exc:
                        logger.warning(f"Failed to memorize event: {exc}")

    async def search_memory(self, user_id: str, query: str, k: int = 5) -> List[dict]:
        """Search user memories using rag-server. If the server is unreachable or errors, log a warning and return an empty list."""

        url = f"{self.base_url}/search_memories"
        payload = {"user_id": user_id, "query": query, "limit": k}
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, timeout=30.0)
                response.raise_for_status()
                data = response.json()
            return data.get("results", [])
        except Exception as exc:
            logger.warning(f"Failed to search memories: {exc}")
            return []

