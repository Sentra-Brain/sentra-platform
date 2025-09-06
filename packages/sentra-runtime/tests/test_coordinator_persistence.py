import pytest

from sentra.runtime.agents.coordinator import CoordinatorAgent
from sentra.runtime.models import EngineEvent, ConversationRequest


class DummySink:
    def __init__(self):
        self.events = []

    async def on_event(self, event: EngineEvent) -> None:
        self.events.append(event)


class StubSentraAgent:
    async def run(self, request: ConversationRequest):
        yield EngineEvent(type="message_delta", content="hi", step_id="s1")
        yield EngineEvent(type="message_final", content="bye", step_id="s1")


@pytest.mark.asyncio
async def test_coordinator_emits_and_sinks_events(monkeypatch):
    # Monkeypatch the SentraAgent used *inside* coordinator
    monkeypatch.setattr(
        "sentra.runtime.agents.coordinator.SentraAgent", StubSentraAgent
    )

    sink = DummySink()
    agent = CoordinatorAgent(sink=sink)
    req = ConversationRequest(messages=["hello there"])

    collected = []
    async for ev in agent.run(req):
        collected.append(ev)

    assert [e.content for e in collected] == ["hi", "bye"]
    assert [e.content for e in sink.events] == ["hi", "bye"]
