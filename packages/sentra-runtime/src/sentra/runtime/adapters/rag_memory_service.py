# packages/sentra-runtime/src/sentra/runtime/adapters/rag_memory_service.py
from __future__ import annotations

"""Implementation of :class:`MemoryService` backed by sentra-rag-server.

Updated to consume an ADK ``Session`` (or ``SupportsSession``) instead of the
removed legacy ``SessionModel``. The ADK ``Session`` exposes ``id`` instead of
``session_id`` and stores a list of ADK ``Event`` objects in ``events``.
"""

from typing import List, Any

import httpx

from sentra.shared.logging import get_logger
from sentra.shared.settings import settings

from sentra.runtime.ports.memory_service import MemoryService, SupportsSession


logger = get_logger(__name__)


class RagMemoryService(MemoryService):
    """Memory service delegating persistence and search to ``rag-server``."""

    def __init__(self) -> None:
        self.base_url = settings.rag_server_url.rstrip("/")

    async def add_session_to_memory(self, session: SupportsSession) -> None:
        """Send assistant "final" message events from ``session`` to rag-server.

        We attempt to be defensive about Event content structure to accommodate
        both ADK Events (which may expose structured ``content``/``parts``) and
        any lingering legacy placeholders during rollout.
        """

        events = getattr(session, "events", None)
        if not events:
            return

        url = f"{self.base_url}/memorize"

        def _extract_text(event: Any) -> str | None:
            content = getattr(event, "content", None)
            # ADK Event.content may already be a string
            if isinstance(content, str):
                return content
            # If content has parts (e.g. content.parts -> list of objects with text)
            parts = getattr(content, "parts", None) if content else None
            if parts and isinstance(parts, (list, tuple)):
                texts: list[str] = []
                for p in parts:
                    # common attributes or dict keys
                    if isinstance(p, str):
                        texts.append(p)
                    else:
                        txt = getattr(p, "text", None)
                        if txt is None and isinstance(p, dict):
                            txt = p.get("text") or p.get("content")
                        if txt:
                            texts.append(str(txt))
                if texts:
                    return "\n".join(texts)
            # Fallback: stringify the content / event
            if content is not None:
                return str(content)
            return None

        async with httpx.AsyncClient() as client:
            for event in events:
                try:
                    event_type = getattr(event, "type", None)
                    author = getattr(event, "author", None) or getattr(getattr(event, "meta", None), "get", lambda *_: None)("author")
                    if event_type in ("message_final", "MESSAGE_FINAL") and author in (None, "assistant"):
                        text = _extract_text(event)
                        if not text:
                            continue
                        payload = {
                            "user_id": getattr(session, "user_id", None),
                            # ADK Session uses "id" for session identifier
                            "session_id": getattr(session, "id", None),
                            "text": text,
                        }
                        await client.post(url, json=payload, timeout=10.0)
                except Exception as exc:  # pragma: no cover - defensive logging
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

