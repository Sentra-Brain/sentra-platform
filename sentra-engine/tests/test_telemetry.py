import logging

import pytest

from sentra_engine.agents.sentra_agent import SentraAgent
from sentra_engine.agents.coordinator import CoordinatorAgent
from sentra_engine.models import ConversationRequest
from sentra_engine import config


@pytest.mark.anyio
async def test_agent_emits_telemetry(caplog):
    config.settings.use_dummy = True
    agent = SentraAgent()
    req = ConversationRequest(messages=["hi there"])
    with caplog.at_level(logging.INFO, logger="sentra_engine.telemetry"):
        async for _ in agent.run(req):
            pass
    event_types = [rec.__dict__.get("type") for rec in caplog.records if rec.msg == "event"]
    assert "agent_started" in event_types
    assert "llm_called" in event_types
    assert "agent_completed" in event_types


@pytest.mark.anyio
async def test_coordinator_fallback_event(caplog):
    config.settings.use_dummy = True
    coord = CoordinatorAgent()
    req = ConversationRequest(messages=["just chatting"])
    with caplog.at_level(logging.INFO, logger="sentra_engine.telemetry"):
        async for _ in coord.run(req):
            pass
    event_types = [rec.__dict__.get("type") for rec in caplog.records if rec.msg == "event"]
    assert "fallback_triggered" in event_types
