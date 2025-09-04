from __future__ import annotations

"""Abstract interface for user memory operations."""

from abc import ABC, abstractmethod

from sentra_core.domain.session_entity import SessionEntity


class MemoryService(ABC):
    """Service responsible for persisting and retrieving long-term memories."""

    @abstractmethod
    async def add_session_to_memory(self, session: SessionEntity) -> None:
        """Extract relevant events from ``session`` and store them as memories."""

    @abstractmethod
    async def search_memory(self, user_id: str, query: str, k: int = 5) -> list[dict]:
        """Search stored memories for ``user_id`` using ``query`` and return top ``k`` results."""

