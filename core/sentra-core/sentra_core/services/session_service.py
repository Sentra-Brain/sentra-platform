from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from sentra_core.domain.event_entity import EventEntity
from sentra_core.domain.session_entity import SessionEntity


class SessionService(ABC):
    """Abstract interface for session persistence compatible with ADK."""

    @abstractmethod
    async def create_session(
        self,
        app_name: str,
        user_id: str,
        session_id: str,
        state: dict[str, Any] | None = None,
    ) -> SessionEntity:
        """Create a new session scratchpad."""

    @abstractmethod
    async def get_session(
        self, app_name: str, user_id: str, session_id: str
    ) -> SessionEntity:
        """Retrieve an existing session."""

    @abstractmethod
    async def append_event(self, session: SessionEntity, event: EventEntity) -> EventEntity:
        """Persist an event and update session state."""

    @abstractmethod
    async def delete_session(self, app_name: str, user_id: str, session_id: str) -> None:
        """Remove a session and its events."""
