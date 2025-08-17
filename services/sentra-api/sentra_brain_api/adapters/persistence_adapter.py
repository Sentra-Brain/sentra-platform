# sentra_brain_api/adapters/persistence_adapter.py
import asyncio
from collections import OrderedDict
from collections.abc import Mapping
from typing import Any, Sequence
from uuid import uuid4

from sentra_engine.ports.persistence import PersistencePort
from sentra_engine.core.models import Message, StepEvent
from sentra_engine.core.constants import CONTEXT_WINDOW_SIZE

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

def _message_to_store(m: Message) -> dict[str, Any]:
    return {
        "id": m.id,
        "role": m.role,
        "content": m.content,
        "timestamp": m.timestamp,
        "meta": m.meta,
    }

def _dict_to_message(d: Mapping[str, Any]) -> Message:
    return Message(
        id=str(d.get("id") or uuid4().hex),
        role=str(d.get("role") or "system"),
        content=str(d.get("content") or ""),
        timestamp=d.get("timestamp"),
        meta=d.get("meta"),
    )

# ---- adapter ----------------------------------------------------------------

class MongoPersistenceAdapter(PersistencePort):
    def __init__(self, *, repo, user_id: str):
        self.repo = repo
        self.user_id = user_id

    async def append_message(self, conversation_id: str, message: Message) -> None:
        payload = _message_to_store(message)
        # persist
        await asyncio.to_thread(
            self.repo.append_message,
            conversation_id=conversation_id,
            user_id=self.user_id,
            message=payload,
        )
        # update cache (append + trim)
        key = _cache_key(self.user_id, conversation_id)
        cached = await _CONV_CACHE.get(key)
        if cached is None:
            # lazy load then update (avoids desync on first write)
            cached = await self.load_conversation(conversation_id)
        # append & trim window
        cached = [*cached, message][-CONTEXT_WINDOW_SIZE:]
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
            raw = (doc.get("messages") or [])  # type: ignore[assignment]
        elif isinstance(doc, (list, tuple)):
            raw = doc  # repo returned the message list directly
        else:
            raw = [] 
        out: list[Message] = []

        for m in raw:
            if isinstance(m, Message):
                out.append(m)
            elif isinstance(m, Mapping):
                out.append(_dict_to_message(m))
            elif hasattr(m, "model_dump"):  # pydantic v2
                out.append(_dict_to_message(m.model_dump()))  # type: ignore[attr-defined]
            elif hasattr(m, "dict"):        # pydantic v1
                out.append(_dict_to_message(m.dict()))        # type: ignore[attr-defined]
            else:
                try:
                    d = vars(m)
                    if isinstance(d, dict):
                        out.append(_dict_to_message(d))
                        continue
                except Exception:
                    pass
                out.append(Message(id=uuid4().hex, role="system", content=str(m)))

        # trim to context window and cache
        out = out[-CONTEXT_WINDOW_SIZE:]
        await _CONV_CACHE.put(key, out)
        return out
