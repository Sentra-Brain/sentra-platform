import logging
import pytest

from sentra.runtime.agents.sentra_agent import SentraAgent
from sentra.runtime.agents.coordinator import CoordinatorAgent
from sentra.runtime.models import ConversationRequest
from sentra.runtime import config


@pytest.mark.anyio
async def test_agent_emits_telemetry(caplog, monkeypatch):
    # Make ADK Runner produce an async stream of events
    class _Part:
        def __init__(self, text): self.text = text

    class _Content:
        def __init__(self, parts): self.parts = parts

    class _Ev:
        def __init__(self, texts, final=False):
            self.content = _Content([_Part(t) for t in texts])
            self._final = final
        def is_final_response(self): return self._final

    async def fake_run_async(*args, **kwargs):
        yield _Ev(["hello"])            # delta
        yield _Ev([], final=True)       # final

    # Patch the specific Runner used inside SentraAgent
    monkeypatch.setattr(
        "sentra.runtime.agents.sentra_agent.Runner.run_async",
        lambda self, *a, **kw: fake_run_async(*a, **kw),
    )

    config.settings.use_dummy = True  # harmless now
    agent = SentraAgent()
    req = ConversationRequest(messages=["hi there"])

    with caplog.at_level(logging.INFO, logger="sentra.runtime.telemetry"):
        async for _ in agent.run(req):
            pass

    event_types = [rec.__dict__.get("type") for rec in caplog.records if rec.msg == "event"]
    assert {"agent_started", "llm_called", "agent_completed"} <= set(event_types)


@pytest.mark.anyio
async def test_coordinator_fallback_event(caplog, monkeypatch):
    # Prevent Coordinator from entering the real SentraAgent runner
    async def noop_run(self, request):
        if False:
            yield  # make it an async generator

    monkeypatch.setattr(
        "sentra.runtime.agents.coordinator.SentraAgent.run",
        noop_run,
    )

    config.settings.use_dummy = True
    coord = CoordinatorAgent()
    req = ConversationRequest(messages=["just chatting"])

    with caplog.at_level(logging.INFO, logger="sentra.runtime.telemetry"):
        async for _ in coord.run(req):
            pass

    event_types = [rec.__dict__.get("type") for rec in caplog.records if rec.msg == "event"]
    assert "fallback_triggered" in event_types
