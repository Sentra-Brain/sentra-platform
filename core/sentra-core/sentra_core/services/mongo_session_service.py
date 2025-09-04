from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from google.adk.events.event import Event
from google.adk.sessions.session import Session
from pymongo import MongoClient

from sentra_core.infra.nosql.mongo_settings import settings

from .session_service import SessionService


class MongoSessionService(SessionService):
    """MongoDB-backed implementation of :class:`SessionService`."""

    def __init__(self, client: MongoClient | None = None) -> None:
        mongo_url = settings.mongo_url or f"mongodb://{settings.mongo_host}:{settings.mongo_port}"
        self.client = client or MongoClient(mongo_url, uuidRepresentation="standard")
        self.db = self.client[settings.mongo_database]
        self.sessions = self.db["sessions"]
        self.user_states = self.db["user_states"]
        self.app_states = self.db["app_states"]

    async def create_session(
        self,
        app_name: str,
        user_id: str,
        session_id: str,
        state: dict[str, Any] | None = None,
    ) -> Session:
        """Create a new session document and return an ADK :class:`Session`."""
        now = datetime.now(timezone.utc)
        state = state or {}
        user_doc = self.user_states.find_one({"_id": user_id})
        if not user_doc:
            user_doc = {"_id": user_id, "state": {}}
            self.user_states.insert_one(user_doc)
        app_doc = self.app_states.find_one({"_id": app_name})
        if not app_doc:
            app_doc = {"_id": app_name, "state": {}}
            self.app_states.insert_one(app_doc)
        session_state = {
            "session": state,
            "user": user_doc.get("state", {}),
            "app": app_doc.get("state", {}),
        }
        doc = {
            "_id": session_id,
            "app_name": app_name,
            "user_id": user_id,
            "session_id": session_id,
            "last_update_time": now,
            "state": session_state,
            "events": [],
        }
        self.sessions.insert_one(doc)
        return Session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
            state=session_state,
            events=[],
        )

    async def get_session(self, app_name: str, user_id: str, session_id: str) -> Session:
        doc = self.sessions.find_one(
            {"_id": session_id, "app_name": app_name, "user_id": user_id}
        )
        if not doc:
            user_doc = self.user_states.find_one({"_id": user_id}) or {"state": {}}
            app_doc = self.app_states.find_one({"_id": app_name}) or {"state": {}}
            state = {
                "session": {},
                "user": user_doc.get("state", {}),
                "app": app_doc.get("state", {}),
            }
            return Session(
                app_name=app_name,
                user_id=user_id,
                session_id=session_id,
                state=state,
                events=[],
            )
        return Session(
            app_name=doc["app_name"],
            user_id=doc["user_id"],
            session_id=doc["session_id"],
            state=doc.get("state", {}),
            events=doc.get("events", []),
        )

    async def append_event(self, session: Session, event: Event) -> Event:
        event_doc = {
            "event_id": str(getattr(event, "event_id", uuid4())),
            "timestamp": getattr(event, "timestamp", datetime.now(timezone.utc)),
            "type": getattr(event, "type", None),
            "author": getattr(event, "author", None),
            "content": getattr(event, "content", None),
        }
        actions = getattr(event, "actions", None)
        state_delta = getattr(actions, "state_delta", None) if actions else None
        if state_delta:
            event_doc["actions"] = {"state_delta": state_delta}
            self._apply_state_delta(session, state_delta)
        message = getattr(event, "message", None)
        if message:
            event_doc["message"] = {
                "id": getattr(message, "id", None),
                "role": getattr(message, "role", None),
                "response_to": getattr(message, "response_to", None),
            }
        now = datetime.now(timezone.utc)
        self.sessions.update_one(
            {"_id": session.session_id},
            {
                "$push": {"events": event_doc},
                "$set": {"state": session.state, "last_update_time": now},
            },
            upsert=True,
        )
        return event

    def _apply_state_delta(self, session: Session, delta: dict[str, Any]) -> None:
        for key, value in delta.items():
            if key.startswith("user:"):
                bare = key.split("user:", 1)[1]
                session.state.setdefault("user", {})[bare] = value
                self.user_states.update_one(
                    {"_id": session.user_id},
                    {"$set": {f"state.{bare}": value}},
                    upsert=True,
                )
            elif key.startswith("app:"):
                bare = key.split("app:", 1)[1]
                session.state.setdefault("app", {})[bare] = value
                self.app_states.update_one(
                    {"_id": session.app_name},
                    {"$set": {f"state.{bare}": value}},
                    upsert=True,
                )
            elif key.startswith("temp:"):
                # Ephemeral state is not persisted
                continue
            else:
                session.state.setdefault("session", {})[key] = value

    async def delete_session(
        self, app_name: str, user_id: str, session_id: str
    ) -> None:
        self.sessions.delete_one(
            {"_id": session_id, "app_name": app_name, "user_id": user_id}
        )
