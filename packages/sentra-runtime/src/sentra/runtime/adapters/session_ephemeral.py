from __future__ import annotations
from typing import Any, Dict, List, Optional
from google.adk.sessions import BaseSessionService, Session
from google.adk.sessions.base_session_service import ListSessionsResponse

class EphemeralSessionService(BaseSessionService):
    """
    In-memory SessionService that satisfies ADK expectations during a single run.
    No DB. Stores events/state only in-process while run() executes.
    """
    def __init__(self, session: Session):
        self._session = session
        self._events: List[Dict[str, Any]] = []

    async def create_session(self, app_name: str, user_id: str, session_id: str, state=None):
        return self._session

    async def get_session(self, app_name: str, user_id: str, session_id: str):
        return self._session

    async def list_sessions(self, *, app_name: str, user_id: str) -> ListSessionsResponse:
        return ListSessionsResponse(sessions=[self._session])

    async def append_event(self, session: Session, event: Dict[str, Any]):
        # Keep ephemeral history + merge state deltas if present
        self._events.append(event)
        actions = event.get("actions") or {}
        delta = actions.get("state_delta") or actions.get("stateDelta") or {}
        if delta:
            s = self._session.state.setdefault("session", {})
            u = self._session.state.setdefault("user", {})
            a = self._session.state.setdefault("app", {})
            for k, v in delta.items():
                if k.startswith("user:"):
                    u[k.split("user:", 1)[1]] = v
                elif k.startswith("app:"):
                    a[k.split("app:", 1)[1]] = v
                elif k.startswith("temp:"):
                    continue
                else:
                    s[k] = v
        return event

    async def delete_session(self, app_name: str, user_id: str, session_id: str):
        return None
