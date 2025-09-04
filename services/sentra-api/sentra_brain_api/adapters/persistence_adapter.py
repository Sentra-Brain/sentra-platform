# sentra_brain_api/adapters/persistence_adapter.py
import asyncio
from collections import OrderedDict
from collections.abc import Mapping
from typing import Any, Sequence
from uuid import uuid4

from sentra_engine.persistence.ports.persistence import PersistencePort
from sentra_engine.core.models import Message, StepEvent
from sentra_engine.core.constants import CONTEXT_WINDOW_SIZE
from sentra_core.schemas.engine_event import EngineEvent

# ---- LRU cache (conversations) ---------------------------------------------

class _LRU:
    def __init__(self, capacity: int = 256):
        self.capacity = capacity
        self._lock = asyncio.Lock()
        self._od: OrderedDict[str, list[Message]] = OrderedDict()

    async def get(self, key: str) -> list[Message] | None:
        async with self._lock:
            if key not in self._od:
                return None
            self._od.move_to_end(key)
            return self._od[key]

    async def put(self, key: str, value: list[Message]) -> None:
        async with self._lock:
            self._od[key] = value
            self._od.move_to_end(key)
            if len(self._od) > self.capacity:
                self._od.popitem(last=False)

    async def invalidate(self, key: str) -> None:
        async with self._lock:
            self._od.pop(key, None)

_CONV_CACHE = _LRU(capacity=256)  # ~256 hot conversations per process

def _cache_key(user_id: str, conversation_id: str) -> str:
    return f"{user_id}:{conversation_id}"

# ---- helpers ----------------------------------------------------------------

def _event_to_payload(e: EngineEvent) -> dict[str, Any]:
    data = e.model_dump(exclude_none=True)
    data["event_id"] = str(e.event_id)
    data["timestamp"] = e.timestamp.isoformat()
    return data

def _event_to_message(e: EngineEvent) -> Message:
    msg = e.message
    return Message(
        id=str(msg.id if msg and msg.id else e.event_id.hex),
        role=str(msg.role if msg and msg.role else e.author),
        content=str(e.content or ""),
        timestamp=e.timestamp.isoformat(),
        meta=e.meta,
    )

def _dict_to_message(d: Mapping[str, Any]) -> Message:
    msg = d.get("message") or {}
    return Message(
        id=str(msg.get("id") or d.get("event_id") or uuid4().hex),
        role=str(msg.get("role") or d.get("author") or "system"),
        content=str(d.get("content") or ""),
        timestamp=d.get("timestamp"),
        meta=d.get("meta"),
    )

# ---- adapter ----------------------------------------------------------------

class MongoPersistenceAdapter(PersistencePort):
    def __init__(self, *, repo, user_id: str):
        self.repo = repo
        self.user_id = user_id

    async def append_event(self, conversation_id: str, event: EngineEvent) -> None:
        payload = _event_to_payload(event)
        await asyncio.to_thread(
            self.repo.append_event,
            session_id=conversation_id,
            user_id=self.user_id,
            event=payload,
        )

        if event.type in {"message_delta", "message_final"}:
            msg = _event_to_message(event)
            key = _cache_key(self.user_id, conversation_id)
            cached = await _CONV_CACHE.get(key)
            if cached is None:
                cached = await self.load_conversation(conversation_id)
            cached = [*cached, msg][-CONTEXT_WINDOW_SIZE:]
            await _CONV_CACHE.put(key, cached)

    async def append_step_event(self, conversation_id: str, event: StepEvent) -> None:
        # Not used in fast mode
        return None

    async def load_conversation(self, conversation_id: str) -> list[Message]:
        key = _cache_key(self.user_id, conversation_id)
        cached = await _CONV_CACHE.get(key)
        if cached is not None:
            return cached

        doc = await asyncio.to_thread(
            self.repo.get_conversation_by_id, conversation_id, self.user_id
        )

        raw: Sequence[Any]
        if isinstance(doc, Mapping):
            raw = doc.get("events") or []  # type: ignore[assignment]
        else:
            raw = []

        out: list[Message] = []
        for e in raw:
            if isinstance(e, Mapping) and e.get("type") == "message_final":
                out.append(_dict_to_message(e))

        out = out[-CONTEXT_WINDOW_SIZE:]
        await _CONV_CACHE.put(key, out)
        return out
