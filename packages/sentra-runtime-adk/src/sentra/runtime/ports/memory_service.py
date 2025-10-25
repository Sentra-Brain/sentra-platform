# packages/sentra-runtime/src/sentra/runtime/ports/memory_service.py
from __future__ import annotations

"""Abstract interface for user memory operations.

Legacy ``SessionModel`` has been removed. Implementations should now accept an
ADK ``Session`` (``google.adk.sessions.Session``) or any object providing the
minimal attributes accessed here (``id``, ``user_id`` and ``events``).
To avoid importing the heavy ADK symbols at interface load time we use a
``Protocol`` describing the required shape. This keeps typing benefits without
creating a hard dependency for test doubles.
"""

from abc import ABC, abstractmethod
from typing import Protocol, Iterable, Any


class SupportsSession(Protocol):  # pragma: no cover - structural typing only
    """Minimal contract for an ADK Session consumed by memory services.

    Attributes
    -----------
    id: Session identifier (formerly ``session_id`` in legacy model)
    user_id: Identifier of the user owning the session
    events: Iterable of ADK ``Event`` objects (or legacy look‑alikes)
    """

    id: str
    user_id: str
    events: Iterable[Any]


class MemoryService(ABC):
    """Service responsible for persisting and retrieving long-term memories."""

    @abstractmethod
    async def add_session_to_memory(self, session: SupportsSession) -> None:
        """Extract relevant events from ``session`` and store them as memories."""

    @abstractmethod
    async def search_memory(self, user_id: str, query: str, k: int = 5) -> list[dict]:
        """Search stored memories for ``user_id`` using ``query`` and return top ``k`` results."""

