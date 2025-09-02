import pytest

from sentra_engine.agents.coordinator import CoordinatorAgent
from sentra_engine.agents import sentra_agent
from sentra_engine.errors import ToolError
from sentra_engine.models import ConversationRequest
from sentra_engine import config


@pytest.mark.anyio
async def test_coordinator_triggers_fallback(monkeypatch):
    config.settings.use_dummy = True

    async def failing_run(self, request):
        raise ToolError()
        yield  # pragma: no cover - ensure async generator signature

    monkeypatch.setattr(sentra_agent.SentraAgent, "run", failing_run)

    coord = CoordinatorAgent()
    req = ConversationRequest(messages=["hi"])
    events = []
    async for ev in coord.run(req):
        events.append(ev)

    assert [e.type for e in events] == ["step_start", "message_delta", "step_end"]
    assert events[0].task_type == "fallback"
    assert "cannot access external tools" in events[1].content
    assert events[-1].task_type == "fallback"
