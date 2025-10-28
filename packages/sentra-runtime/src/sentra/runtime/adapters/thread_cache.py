from collections import OrderedDict
from asyncio import Lock
from typing import Any

class InMemoryThreadCache:
    """Simple async-safe LRU cache for serialized AgentThread states."""

    def __init__(self, capacity: int = 256):
        self.capacity = capacity
        self._store: OrderedDict[str, dict[str, Any]] = OrderedDict()
        self._lock = Lock()

    async def get(self, key: str) -> dict[str, Any] | None:
        async with self._lock:
            if key not in self._store:
                return None
            self._store.move_to_end(key)
            return self._store[key]

    async def set(self, key: str, value: dict[str, Any]):
        async with self._lock:
            self._store[key] = value
            self._store.move_to_end(key)
            if len(self._store) > self.capacity:
                self._store.popitem(last=False)

    async def delete(self, key: str):
        async with self._lock:
            self._store.pop(key, None)
