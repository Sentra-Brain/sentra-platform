import pytest

from sentra_engine.adapters.persistence_adapter import ConversationPersistenceAdapter
from sentra_engine.models import ConversationEvent


class DummyRepo:
    def __init__(self):
        self.messages = []

    def append_message(self, conversation_id, user_id, message):
        self.messages.append(message)


@pytest.mark.asyncio
async def test_persist_event_idempotent():
    repo = DummyRepo()
    adapter = ConversationPersistenceAdapter(
        repo=repo, user_id="u1", conversation_id="c1"
    )
    event = ConversationEvent(type="message_delta", content="hi", step_id="s1")

    await adapter.persist_event(event)
    await adapter.persist_event(event)  # duplicate

    assert len(repo.messages) == 1
    assert repo.messages[0]["content"] == "hi"
