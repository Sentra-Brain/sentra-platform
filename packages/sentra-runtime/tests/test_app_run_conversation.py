import pytest
import sys

from sentra.runtime.app import run_conversation
from sentra.runtime.models import ConversationRequest

from google.adk.events.event import Event
from google.genai import types


# --- Stub Runner so we don’t depend on vLLM backend in unit tests ---
async def _stub_run_async(*_, **__):
    yield Event(
        author="assistant",
        content=types.Content(role="assistant", parts=[types.Part(text="hello")] ),
        custom_metadata={"type": "message_delta"},
    )
    yield Event(
        author="assistant",
        content=types.Content(role="assistant", parts=[types.Part(text="world")] ),
        custom_metadata={"type": "message_final"},
    )


@pytest.mark.asyncio
async def test_run_conversation_single_agent(monkeypatch):
    # Monkeypatch Runner.run_async to stream stub events
    runners_mod = sys.modules.get("google.adk.runners")
    if runners_mod and hasattr(runners_mod, "Runner"):
        monkeypatch.setattr(runners_mod.Runner, "run_async", _stub_run_async, raising=False)

    # Ensure AgentLoader returns a valid BaseAgent stub
    base_agent_cls = getattr(sys.modules.get("google.adk.agents"), "BaseAgent", object)

    class _FakeAgent(base_agent_cls):  # type: ignore
        pass

    monkeypatch.setattr(
        "sentra.runtime.agents.agent_loader.AgentLoader.load_agent",
        lambda self, name: _FakeAgent(),
    )

    req = ConversationRequest(messages=["hello there"], user_id="u1")
    events = []
    async for ev in run_conversation(req):
        events.append(ev)

    # --- Assertions ---
    assert any(ev.custom_metadata.get("type") == "message_delta" for ev in events)
    assert any(ev.custom_metadata.get("type") == "message_final" for ev in events)
    finals = [ev for ev in events if ev.custom_metadata.get("type") == "message_final"]
    assert finals and finals[0].author == "assistant"
