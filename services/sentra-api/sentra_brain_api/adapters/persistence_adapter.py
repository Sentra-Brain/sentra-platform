"""Persistence adapter used by the API layer.

The engine is persistence-agnostic. The API stores all events in MongoDB
and keeps a small LRU cache of recent messages per conversation so the
engine can be called with a compact context.
"""
from __future__ import annotations

import asyncio
from collections import OrderedDict
from datetime import datetime, timezone
from typing import Any, Mapping, Sequence
from uuid import uuid4

from sentra_core.schemas.engine_event import EngineEvent


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
        self, conversation_id: str, *, text: str, meta: Mapping[str, Any] | None = None
    ) -> None:
        event = EngineEvent(
            event_id=uuid4().hex,
            timestamp=datetime.now(timezone.utc),
            type="message_final",
            author="user",
            content=text,
            meta=dict(meta or {}),
        )
        await asyncio.to_thread(
            self.repo.append_event,
            session_id=conversation_id,
            user_id=self.user_id,
            event=event.model_dump(exclude_none=True),
        )
        key = _cache_key(self.user_id, conversation_id)
        cached = await _CONV_CACHE.get(key) or []
        cached.append(text)
        await _CONV_CACHE.put(key, cached)

    async def append_event(self, conversation_id: str, event: EngineEvent) -> None:
        payload = event.model_dump(exclude_none=True)
        if event.timestamp is not None:
            payload["timestamp"] = event.timestamp.isoformat()
        if event.event_id is not None:
            payload["event_id"] = event.event_id
        await asyncio.to_thread(
            self.repo.append_event,
            session_id=conversation_id,
            user_id=self.user_id,
            event=payload,
        )
        if (
            event.type == "message_final"
            and event.content
            and event.author in {"assistant", "user"}
        ):
            key = _cache_key(self.user_id, conversation_id)
            cached = await _CONV_CACHE.get(key) or []
            cached.append(event.content)
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
                msgs.append(str(e.get("content") or ""))
        msgs = msgs[-limit:]
        await _CONV_CACHE.put(key, msgs)
        return msgs
