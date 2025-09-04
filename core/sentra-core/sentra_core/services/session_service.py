from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from google.adk.events.event import Event
from google.adk.sessions.session import Session


class SessionService(ABC):
    """Abstract interface for session persistence compatible with ADK."""

    @abstractmethod
    async def create_session(
        self,
        app_name: str,
        user_id: str,
        session_id: str,
        state: dict[str, Any] | None = None,
    ) -> Session:
        """Create a new session scratchpad."""

    @abstractmethod
    async def get_session(
        self, app_name: str, user_id: str, session_id: str
    ) -> Session:
        """Retrieve an existing session."""

    @abstractmethod
    async def append_event(self, session: Session, event: Event) -> Event:
        """Persist an event and update session state."""

    @abstractmethod
    async def delete_session(self, app_name: str, user_id: str, session_id: str) -> None:
        """Remove a session and its events."""
