import pytest

from sentra_engine.adapters.persistence_adapter import SessionPersistenceAdapter
from sentra_engine.models import ConversationEvent


class DummyRepo:
    def __init__(self):
        self.events = []

    def append_event(self, session_id, user_id, event):
        self.events.append(event)


@pytest.mark.asyncio
async def test_persist_event_idempotent():
    repo = DummyRepo()
    adapter = SessionPersistenceAdapter(
        repo=repo, user_id="u1", session_id="s1"
    )
    event = ConversationEvent(type="message_delta", content="hi", step_id="s1")

    await adapter.persist_event(event)
    await adapter.persist_event(event)  # duplicate

    assert len(repo.events) == 1
    assert repo.events[0]["content"] == "hi"
