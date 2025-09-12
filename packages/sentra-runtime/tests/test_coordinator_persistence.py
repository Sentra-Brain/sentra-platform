import pytest
from uuid import uuid4

from google.adk.events.event import Event
from google.genai import types
from sentra.runtime.agents.coordinator import CoordinatorAgent
from sentra.runtime.models import ConversationRequest


class DummySink:
    def __init__(self):
        self.events = []

    async def on_event(self, event: Event) -> None:
        self.events.append(event)


class StubSentraAgent:
    async def run(self, request: ConversationRequest, task_run_id: str):
        yield Event(author="assistant", content=types.Content(role="assistant", parts=[types.Part(text="hi")]), custom_metadata={"type": "message_delta"})
        yield Event(author="assistant", content=types.Content(role="assistant", parts=[types.Part(text="bye")]), custom_metadata={"type": "message_delta"})


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

    # Assert assistant deltas came through
    assert [p.text for e in collected if e.author == "assistant" for p in e.content.parts] == ["hi", "bye"]
    assert [p.text for e in sink.events if e.author == "assistant" for p in e.content.parts] == ["hi", "bye"]

