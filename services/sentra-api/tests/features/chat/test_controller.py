import json
from typing import Any
import uuid
from datetime import datetime, timezone

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from sentra.domain.entities.user_entity import UserEntity
from sentra_brain_api.features.chat.controller import ChatController
from sentra_brain_api.crosscutting.authorization import get_authenticated_user
from sentra.infra.nosql.mongo_session_repository import get_session_mongo_repository
from sentra.schemas.engine_event import EngineEvent
from sentra_brain_api.features.chat.mappers import engine_event_to_wire


class DummyAdapter:
    def __init__(self):
        self.call_log = []
        self.recent: list[str] = []

    async def persist_user_message(self, conversation_id, *, text, meta=None):
        self.call_log.append(("persist_user_message", conversation_id, text))

    async def get_recent_context(self, conversation_id, limit):
        self.call_log.append(("get_recent_context", conversation_id, limit))
        return list(self.recent)

    async def append_event(self, conversation_id, event):
        self.call_log.append(("append_event", conversation_id, event))

    async def get_session_state(self, conversation_id: str) -> dict[str, Any] | None:
        self.call_log.append(("get_session_state", conversation_id))
        return {"session": {}, "user": {}, "app": {}}


def parse_sse(text: str):
    events = []
    for line in text.splitlines():
        if line.startswith("data: "):
            raw = line[6:].strip()
            if raw:
                events.append(json.loads(raw))
    return events


@pytest.fixture
def mock_user():
    return UserEntity(id=uuid.uuid4(), username="tester")


@pytest.fixture
def app(mock_user, monkeypatch):
    app = FastAPI()
    app.include_router(ChatController().router, prefix="/chat")
    app.dependency_overrides[get_authenticated_user] = lambda: mock_user
    app.dependency_overrides[get_session_mongo_repository] = lambda: object()
    adapter = DummyAdapter()
    monkeypatch.setattr(
        "sentra_brain_api.features.chat.controller.MongoPersistenceAdapter",
        lambda repo, user_id: adapter,
    )
    return app, adapter


def test_streaming_persists_and_streams_events(app, mock_user, monkeypatch):
    app, adapter = app
    events = [
        EngineEvent(
            event_id=uuid.uuid4().hex,
            timestamp=datetime.now(timezone.utc),
            type="message_delta",
            content="a",
            author="assistant",
        ),
        EngineEvent(
            event_id=uuid.uuid4().hex,
            timestamp=datetime.now(timezone.utc),
            type="message_delta",
            content="b",
            author="assistant",
        ),
        EngineEvent(
            event_id=uuid.uuid4().hex,
            timestamp=datetime.now(timezone.utc),
            type="message_final",
            content="ab",
            author="assistant",
        ),
    ]

    async def fake_run(_req):
        for ev in events:
            yield ev

    monkeypatch.setattr("sentra.runtime.app.run_conversation", fake_run)

    client = TestClient(app)
    payload = {"user_id": str(mock_user.id), "session_id": str(uuid.uuid4()), "content": "hi"}
    resp = client.post("/chat/send", json=payload)
    assert resp.status_code == 200
    parsed = parse_sse(resp.text)
    expected = [engine_event_to_wire(e).model_dump() for e in events]
    assert parsed == expected
    # Persist calls
    assert adapter.call_log[0][0] == "persist_user_message"
    append_calls = [c for c in adapter.call_log if c[0] == "append_event"]
    assert len(append_calls) == 3


def test_user_message_persisted_first(app, mock_user, monkeypatch):
    app, adapter = app
    adapter.call_log.clear()

    async def fake_run(_req):
        yield EngineEvent(
            event_id=uuid.uuid4().hex,
            timestamp=datetime.now(timezone.utc),
            type="message_final",
            content="ok",
            author="assistant",
        )

    monkeypatch.setattr("sentra.runtime.app.run_conversation", fake_run)
    client = TestClient(app)
    payload = {"user_id": str(mock_user.id), "session_id": str(uuid.uuid4()), "content": "hi"}
    client.post("/chat/send", json=payload)
    assert adapter.call_log[0][0] == "persist_user_message"
