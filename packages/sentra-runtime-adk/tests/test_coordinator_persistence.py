import pytest
from uuid import uuid4

from google.adk.events.event import Event
from google.genai import types
from sentra.runtime.agents.coordinator import CoordinatorAgent
from sentra.runtime.agents.agent_loader import AgentLoader  # noqa: F401 (kept for context)
import sys
from sentra.runtime.models import ConversationRequest


class DummySink:
    def __init__(self):
        self.events = []

    async def on_event(self, event: Event) -> None:
        self.events.append(event)


async def _stub_run_async(*_, **__):
    yield Event(author="assistant", content=types.Content(role="assistant", parts=[types.Part(text="hi")]), custom_metadata={"type": "message_delta"})
    yield Event(author="assistant", content=types.Content(role="assistant", parts=[types.Part(text="bye")]), custom_metadata={"type": "message_delta"})
    yield Event(author="assistant", content=types.Content(role="assistant", parts=[types.Part(text="hibye")]), custom_metadata={"type": "message_final"})


@pytest.mark.asyncio
async def test_coordinator_emits_and_sinks_events(monkeypatch):
    # Monkeypatch Runner to bypass model invocation and stream stub events
    runners_mod = sys.modules.get("google.adk.runners")
    if runners_mod and hasattr(runners_mod, "Runner"):
        monkeypatch.setattr(runners_mod.Runner, "run_async", _stub_run_async, raising=False)
    # Ensure AgentLoader returns a valid BaseAgent instance for isinstance check
    base_agent_cls = getattr(sys.modules.get("google.adk.agents"), "BaseAgent", object)
    class _BA(base_agent_cls):  # type: ignore
        pass
    monkeypatch.setattr("sentra.runtime.agents.agent_loader.AgentLoader.load_agent", lambda self, name: _BA())

    sink = DummySink()
    agent = CoordinatorAgent(sink=sink)
    req = ConversationRequest(messages=["hello there"])

    collected = []
    async for ev in agent.run(req):
        collected.append(ev)

    # Final message present & persisted
    finals = [e for e in collected if (e.custom_metadata or {}).get("type") == "message_final"]
    assert finals, "Expected a final assistant event"
    assert any(e in sink.events for e in finals), "Final event not persisted to sink"

