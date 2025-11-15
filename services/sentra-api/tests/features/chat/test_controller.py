# import json
# from typing import Any
# import uuid
# from datetime import datetime, timezone

# import pytest
# from fastapi import FastAPI
# from fastapi.testclient import TestClient

# from sentra.domain.entities.user_entity import UserEntity
# from google.adk.events.event import Event
# from google.genai import types
# from sentra_brain_api.adapters.session_service import get_session_service, APP_NAME
# from sentra_brain_api.crosscutting.authorization import get_authenticated_user
# from sentra.infra.nosql.conversation_mongo_repository import get_session_mongo_repository


# class DummyAdapter:
#     def __init__(self):
#         self.call_log = []
#         self.recent: list[str] = []

#     async def persist_user_message(self, conversation_id, *, text, meta=None):
#         self.call_log.append(("persist_user_message", conversation_id, text))

#     async def get_recent_context(self, conversation_id, limit):
#         self.call_log.append(("get_recent_context", conversation_id, limit))
#         return list(self.recent)

#     async def append_event(self, conversation_id, event):
#         self.call_log.append(("append_event", conversation_id, event))

#     async def get_session_state(self, conversation_id: str) -> dict[str, Any] | None:
#         self.call_log.append(("get_session_state", conversation_id))
#         return {"session": {}, "user": {}, "app": {}}


# def parse_sse(text: str):
#     events = []
#     for line in text.splitlines():
#         if line.startswith("data: "):
#             raw = line[6:].strip()
#             if raw:
#                 events.append(json.loads(raw))
#     return events


# @pytest.fixture
# def mock_user():
#     return UserEntity(id=uuid.uuid4(), username="tester")


# @pytest.fixture
# def app(mock_user, monkeypatch):
#     app = FastAPI()
#     # app.include_router(ChatController().router, prefix="/chat")
#     app.dependency_overrides[get_authenticated_user] = lambda: mock_user
#     app.dependency_overrides[get_session_mongo_repository] = lambda: object()
#     adapter = DummyAdapter()
#     monkeypatch.setattr(
#         # "sentra_brain_api.features.chat.controller.MongoPersistenceAdapter",
#         lambda repo, user_id: adapter,
#     )
#     return app, adapter


# def test_streaming_persists_and_streams_events(app, mock_user, monkeypatch):
#     app, adapter = app
#     def _evt(txt: str, t: str):
#         e = Event(author="assistant", content=types.Content(role="assistant", parts=[types.Part(text=txt)]), custom_metadata={"type": t})
#         return e
#     events = [
#         _evt("a", "message_delta"),
#         _evt("b", "message_delta"),
#         _evt("ab", "message_final"),
#     ]

#     async def fake_run(_req):
#         for ev in events:
#             yield ev

#     monkeypatch.setattr("sentra.runtime.app.run_conversation", fake_run)

#     client = TestClient(app)
#     # Omit session_id to force creation
#     payload = {"user_id": str(mock_user.id), "content": "hi"}
#     resp = client.post("/chat/send", json=payload)
#     assert resp.status_code == 200
#     parsed = parse_sse(resp.text)
#     # First event should include session_id field
#     assert "session_id" in parsed[0]
#     session_id = parsed[0]["session_id"]
#     # Remove session_id for comparison of event payloads
#     comparable = []
#     for p in parsed:
#         cp = dict(p)
#         cp.pop("session_id", None)
#         comparable.append(cp)
#     expected = [e.model_dump(by_alias=True) for e in events]
#     assert comparable == expected
#     # Persist calls
#     assert adapter.call_log[0][0] == "persist_user_message"
#     append_calls = [c for c in adapter.call_log if c[0] == "append_event"]
#     assert len(append_calls) == 3


# def test_user_message_persisted_first(app, mock_user, monkeypatch):
#     app, adapter = app
#     adapter.call_log.clear()

#     async def fake_run(_req):
#         yield Event(author="assistant", content=types.Content(role="assistant", parts=[types.Part(text="ok")]), custom_metadata={"type": "message_final"})

#     monkeypatch.setattr("sentra.runtime.app.run_conversation", fake_run)
#     client = TestClient(app)
#     payload = {"user_id": str(mock_user.id), "content": "hi"}
#     client.post("/chat/send", json=payload)
#     assert adapter.call_log[0][0] == "persist_user_message"


# def test_streaming_generates_missing_fields(app, mock_user, monkeypatch):
#     """Engine events missing identifiers should still stream correctly."""
#     app, adapter = app
#     adapter.call_log.clear()

#     events = [Event(author="assistant", content=types.Content(role="assistant", parts=[types.Part(text="ok")]), custom_metadata={"type": "message_final"})]

#     async def fake_run(_req):
#         for ev in events:
#             yield ev

#     monkeypatch.setattr("sentra.runtime.app.run_conversation", fake_run)

#     client = TestClient(app)
#     payload = {"user_id": str(mock_user.id), "content": "hi"}
#     resp = client.post("/chat/send", json=payload)
#     assert resp.status_code == 200

#     parsed = parse_sse(resp.text)
#     assert len(parsed) == 1
#     evt = parsed[0]
#     assert "session_id" in evt
#     # Strip session_id for remaining assertions
#     sid = evt.pop("session_id")
#     assert isinstance(sid, str) and len(sid) > 0
#     assert evt["type"] in ("message_final", "message_delta")
#     assert "event_id" in evt and "timestamp" in evt

#     # ensure persisted event got populated fields
#     append_calls = [c for c in adapter.call_log if c[0] == "append_event"]
#     assert len(append_calls) == 1
#     stored_evt = append_calls[0][2]
#     assert stored_evt.id == evt["event_id"] or stored_evt.id == evt.get("id")
