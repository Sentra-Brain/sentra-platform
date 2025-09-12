# services/sentra-api/sentra_brain_api/adapters/persistence_adapter.py
"""Persistence adapter used by the API layer.

The engine is persistence-agnostic. The API stores all events in MongoDB
and keeps a small LRU cache of recent messages per conversation so the
engine can be called with a compact context.
"""
from __future__ import annotations

import asyncio
from collections import OrderedDict
from typing import Any, Mapping, Sequence
from uuid import uuid4, UUID

from google.adk.events.event import Event
from google.genai import types
from sentra.shared.logging import get_logger

logger = get_logger("sentra_brain_api.chat.v2")

# ---- LRU cache ---------------------------------------------------------------

class _LRU:
    def __init__(self, capacity: int = 256):
        self.capacity = capacity
        self._lock = asyncio.Lock()
        self._od: OrderedDict[str, list[str]] = OrderedDict()

    async def get(self, key: str) -> list[str] | None:
        async with self._lock:
            if key not in self._od:
                return None
            self._od.move_to_end(key)
            return self._od[key]

    async def put(self, key: str, value: list[str]) -> None:
        async with self._lock:
            self._od[key] = value
            self._od.move_to_end(key)
            if len(self._od) > self.capacity:
                self._od.popitem(last=False)


_CONV_CACHE = _LRU(capacity=256)


def _cache_key(user_id: str, conversation_id: str) -> str:
    return f"{user_id}:{conversation_id}"


# ---- adapter -----------------------------------------------------------------

class MongoPersistenceAdapter:
    """Persist conversation events and maintain a recent context cache."""

    def __init__(self, *, repo, user_id: str):
        self.repo = repo
        self.user_id = user_id

    async def persist_user_message(
        self, conversation_id: str, *, text: str, event_id: UUID
    ) -> None:
        event = Event(author="user", content=types.Content(role="user", parts=[types.Part(text=text)]), custom_metadata={"type": "message_final"})
        # override generated id with client-provided id
        event.id = str(event_id)
        payload = event.model_dump(exclude_none=True)
        payload["id"] = event.id
        payload["event_id"] = event.id
        payload["timestamp"] = payload.get("timestamp") or event.timestamp
        md = event.custom_metadata or {}
        payload.update({k: v for k, v in md.items() if k not in payload})
        payload["type"] = md.get("type") or ("message_final" if event.is_final_response() else "message_delta")

        await asyncio.to_thread(
            self.repo.append_event,
            session_id=conversation_id,
            user_id=self.user_id,
            event=payload,
        )
        key = _cache_key(self.user_id, conversation_id)
        cached = await _CONV_CACHE.get(key) or []
        cached.append(text)
        await _CONV_CACHE.put(key, cached)

    async def append_event(self, conversation_id: str, event: Event) -> None:
        payload = event.model_dump(exclude_none=True)
        payload["id"] = event.id
        payload.setdefault("event_id", event.id)
        payload["timestamp"] = payload.get("timestamp") or event.timestamp
        md = event.custom_metadata or {}
        payload.update({k: v for k, v in md.items() if k not in payload})
        payload["type"] = md.get("type") or ("message_final" if event.is_final_response() else "message_delta")
        await asyncio.to_thread(
            self.repo.append_event,
            session_id=conversation_id,
            user_id=self.user_id,
            event=payload,
        )
        # Update LRU cache only for final user/assistant messages
        if (
            payload.get("type") == "message_final"
            and event.content
            and event.author in {"assistant", "user"}
        ):
            # Extract text safely
            text = None
            if event.content and event.content.parts:
                first = event.content.parts[0]
                if getattr(first, "text", None):
                    text = first.text  # type: ignore[attr-defined]

            if text:
                key = _cache_key(self.user_id, conversation_id)
                cached = await _CONV_CACHE.get(key) or []
                cached.append(text)
                await _CONV_CACHE.put(key, cached)

    async def get_recent_context(self, conversation_id: str, limit: int) -> list[str]:
        key = _cache_key(self.user_id, conversation_id)
        cached = await _CONV_CACHE.get(key)
        if cached is not None:
            return cached[-limit:]

        doc = await asyncio.to_thread(
            self.repo.get_session_by_id, conversation_id, self.user_id
        )
        raw: Sequence[Any] = doc.get("events", []) if isinstance(doc, Mapping) else []
        msgs: list[str] = []
        for e in raw:
            if (
                isinstance(e, Mapping)
                and e.get("type") == "message_final"
                and e.get("author") in {"assistant", "user"}
            ):
                content = e.get("content")
                text_val = None
                if isinstance(content, Mapping):
                    parts = content.get("parts")
                    if isinstance(parts, list) and parts:
                        first = parts[0]
                        if isinstance(first, Mapping):
                            text_val = first.get("text")
                if not text_val and content is not None:
                    # fallback to string conversion
                    text_val = str(content)
                if text_val:
                    msgs.append(text_val)
        msgs = msgs[-limit:]
        await _CONV_CACHE.put(key, msgs)
        return msgs
    
    async def get_session_state(self, conversation_id: str) -> dict[str, Any] | None:
        try:
            doc = await asyncio.to_thread(
                self.repo.get_session_by_id, conversation_id, self.user_id
            )
            return (doc or {}).get("state", {"session": {}, "user": {}, "app": {}})
        except Exception:
            logger.exception("Failed to get session state")
            return {"session": {}, "user": {}, "app": {}}
