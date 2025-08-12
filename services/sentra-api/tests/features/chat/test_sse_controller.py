# tests/features/chat/test_chat_controller_sse.py

import json
import uuid
import types
import pytest
from unittest.mock import patch
from fastapi import FastAPI
from fastapi.testclient import TestClient

from sentra_brain_api.features.chat.controller import ChatController
from sentra_brain_api.crosscutting.authorization import get_authenticated_user
from sentra_core.domain.entities.user_entity import UserEntity
from sentra_brain_api.core.conversation_engine.models.output_model import ConversationEvent


@pytest.fixture
def mock_user():
    # Realistic user entity (SQLAlchemy model); only fields we need here
    return UserEntity(id=uuid.uuid4(), username="testuser")


@pytest.fixture
def app(mock_user):
    app = FastAPI()
    app.include_router(ChatController().router, prefix="/chat")
    # Auth override
    app.dependency_overrides[get_authenticated_user] = lambda: mock_user
    return app


def parse_sse(text: str):
    events = []
    for line in text.split("\n"):
        if line.startswith("data: "):
            raw = line[6:].strip()
            if not raw:
                continue
            try:
                events.append(json.loads(raw))
            except json.JSONDecodeError:
                # ignore keep-alives or stray lines
                pass
    return events


def make_evt(**kwargs) -> ConversationEvent:
    # Helper to ensure every event is a valid ConversationEvent
    base = {"type": "message_delta", "content": "x"}
    base.update(kwargs)
    return ConversationEvent(**base) # type: ignore[call-arg]


def test_sse_with_rag_events_and_user_override(app, mock_user):
    # Capture the user_id that reaches the engine to confirm override works
    seen_user_ids = []

    async def fake_run(request):
        # controller must have overwritten request.user_id with mock_user.id
        seen_user_ids.append(str(request.user_id))

        # Only emit step events if RAG context is present (mirrors real behavior)
        if request.context_source_ids:
            run_id = uuid.uuid4().hex
            yield make_evt(
                type="step_start",
                task_type="rag_search",
                task_run_id=run_id,
                label="Searching Knowledge Base",
                status="searching",
                content="Searching..."
            )
            yield make_evt(
                type="step_end",
                task_type="rag_search",
                task_run_id=run_id,
                label="Knowledge Base Search Complete",
                status="completed",
                content="Found 2 chunks",
                meta={"chunks_found": 2}
            )
        yield make_evt(type="message_delta", content="Hello ")
        yield make_evt(type="message_delta", content="world!")
        yield make_evt(type="message_final", content="")

    # Patch app.state._sentra to provide a fake engine with our run()
    with patch.object(
        app.state,
        "_sentra",
        types.SimpleNamespace(conversation_engine=types.SimpleNamespace(run=fake_run)),
        create=True,
    ):
        client = TestClient(app)

        payload = {
            # ConversationRequest schema: user_id is REQUIRED → include it (will be overridden)
            "user_id": str(uuid.uuid4()),  # intentionally different than mock_user.id
            "conversation_id": str(uuid.uuid4()),
            "message_id": str(uuid.uuid4()),
            "response_message_id": str(uuid.uuid4()),
            "content": "query using RAG",
            # RAG UUID arrays → strings accepted; Pydantic converts to UUID
            "context_source_ids": [str(uuid.uuid4())],
            "context_document_ids": [str(uuid.uuid4())],
        }

        resp = client.post("/chat/send", json=payload)
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "text/event-stream; charset=utf-8"

        events = parse_sse(resp.text)
        assert events, "No SSE events parsed"

        types_ = [e["type"] for e in events]
        assert "step_start" in types_
        assert "step_end" in types_
        assert "message_delta" in types_
        assert "message_final" in types_

        # Required fields present on all events
        for e in events:
            assert e.get("event_id"), "event_id missing"
            assert e.get("timestamp"), "timestamp missing"

        # step fields
        start = next(e for e in events if e["type"] == "step_start")
        end = next(e for e in events if e["type"] == "step_end")
        assert start["task_type"] == "rag_search"
        assert start["status"] == "searching"
        assert end["status"] == "completed"
        assert end["task_run_id"] == start["task_run_id"]
        assert end["meta"]["chunks_found"] == 2

        # Confirm the controller overwrote user_id with the authenticated user
        assert seen_user_ids and seen_user_ids[0] == str(mock_user.id)


def test_sse_without_step_events(app, mock_user):
    async def fake_run(_request):
        yield make_evt(type="message_delta", content="Only text ")
        yield make_evt(type="message_delta", content="stream.")
        yield make_evt(type="message_final", content="")

    with patch.object(
        app.state,
        "_sentra",
        types.SimpleNamespace(conversation_engine=types.SimpleNamespace(run=fake_run)),
        create=True,
    ):
        client = TestClient(app)
        payload = {
            "user_id": str(mock_user.id),  # required by schema
            "conversation_id": str(uuid.uuid4()),
            "message_id": str(uuid.uuid4()),
            "response_message_id": str(uuid.uuid4()),
            "content": "plain query",
            # No RAG context → no step events expected
        }
        resp = client.post("/chat/send", json=payload)
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "text/event-stream; charset=utf-8"

        events = parse_sse(resp.text)
        types_ = [e["type"] for e in events]
        assert "step_start" not in types_
        assert "step_end" not in types_
        assert "message_delta" in types_
        assert "message_final" in types_
        for e in events:
            assert e.get("event_id")
            assert e.get("timestamp")


def test_sse_error_path_emits_step_error(app, mock_user):
    async def fake_run(_request):
        # Make this an async generator, then raise on first iteration
        if False:
            # keep type correct; never executed
            yield ConversationEvent(type="message_delta", content="")
        raise RuntimeError("boom")

    with patch.object(
        app.state,
        "_sentra",
        types.SimpleNamespace(conversation_engine=types.SimpleNamespace(run=fake_run)),
        create=True,
    ):
        client = TestClient(app)
        payload = {
            "user_id": str(mock_user.id),
            "conversation_id": str(uuid.uuid4()),
            "message_id": str(uuid.uuid4()),
            "response_message_id": str(uuid.uuid4()),
            "content": "will fail",
        }
        resp = client.post("/chat/send", json=payload)
        events = parse_sse(resp.text)
        err = events[-1]
        assert err["type"] == "step_error"
        assert "boom" in err.get("content", "")
