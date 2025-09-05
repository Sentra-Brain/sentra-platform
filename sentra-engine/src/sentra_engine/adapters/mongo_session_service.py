from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pymongo import MongoClient

from sentra_core.infra.nosql.mongo_settings import settings
from sentra_core.domain.event_entity import EventEntity, EventMessage
from sentra_core.schemas.engine_event import EngineEvent
from sentra_core.domain.session_entity import SessionEntity

from google.adk.sessions import BaseSessionService
from google.adk.sessions.base_session_service import ListSessionsResponse


class MongoSessionService(BaseSessionService):
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
    ) -> SessionEntity:
        """Create a new session document and return a :class:`SessionEntity`."""
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
        return SessionEntity(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
            state=session_state,
            events=[],
            last_update_time=now,
        )

    async def get_session(self, app_name: str, user_id: str, session_id: str) -> SessionEntity:
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
            return SessionEntity(
                app_name=app_name,
                user_id=user_id,
                session_id=session_id,
                state=state,
                events=[],
                last_update_time=datetime.now(timezone.utc),
            )
        return SessionEntity(
            app_name=doc["app_name"],
            user_id=doc["user_id"],
            session_id=doc["session_id"],
            state=doc.get("state", {}),
            events=[EventEntity(**e) for e in doc.get("events", [])],
            last_update_time=doc.get("last_update_time", datetime.now(timezone.utc)),
        )

    async def list_sessions(
        self, *, app_name: str, user_id: str
    ) -> ListSessionsResponse:
        # Query MongoDB for all sessions for this app and user
        docs = self.sessions.find({"app_name": app_name, "user_id": user_id})
        sessions = []
        for doc in docs:
            # Convert your SessionEntity to ADK's Session model
            session = SessionEntity.model_validate({
                "app_name": doc["app_name"],
                "user_id": doc["user_id"],
                "session_id": doc["session_id"],
                "state": doc.get("state", {}),
                "events": [],  # Per ADK doc, events/states not set in list
                "last_update_time": doc.get("last_update_time"),
            })
            sessions.append(session)
        return ListSessionsResponse(sessions=sessions)
    
    async def append_event(
        self, session: SessionEntity, event: EventEntity | EngineEvent
    ) -> EventEntity | EngineEvent:
        """Persist an ``event`` and merge any state delta."""
        # Ensure backward compatibility for legacy message lookups
        if (
            event.type in {"message_delta", "message_final"}
            and event.author in {"user", "assistant"}
            and event.message is None
        ):
            event.message = EventMessage(
                id=event.event_id,
                role=event.author,
                response_to=event.meta.get("response_to") if event.meta else None,
            )

        event_doc = event.model_dump()
        event_doc["event_id"] = event.event_id

        state_delta = event.actions.state_delta if event.actions else None
        if state_delta:
            self._apply_state_delta(session, state_delta)

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

    def _apply_state_delta(self, session: SessionEntity, delta: dict[str, Any]) -> None:
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
