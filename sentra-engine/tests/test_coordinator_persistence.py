import pytest

from sentra_engine.agents.coordinator import CoordinatorAgent
from sentra_engine.models import ConversationEvent, ConversationRequest


class DummyPersistence:
    def __init__(self):
        self.events = []

    async def persist_event(self, event: ConversationEvent) -> None:
        self.events.append(event)


class StubSentraAgent:
    async def run(self, request: ConversationRequest):
        yield ConversationEvent(type="message_delta", content="hi", step_id="s1")
        yield ConversationEvent(type="message_final", content="bye", step_id="s1")


@pytest.mark.asyncio
async def test_coordinator_persists_events(monkeypatch):
    monkeypatch.setattr(
        "sentra_engine.agents.coordinator.SentraAgent", StubSentraAgent
    )
    persistence = DummyPersistence()
    agent = CoordinatorAgent(persistence=persistence)
    req = ConversationRequest(messages=["hello there"])

    collected = []
    async for ev in agent.run(req):
        collected.append(ev)

    assert [e.content for e in collected] == ["hi", "bye"]
    assert [e.content for e in persistence.events] == ["hi", "bye"]
