import anyio
import importlib


def test_run_conversation_streams_dummy_events(monkeypatch):
    import sentra_engine.models as models
    import sentra_engine.app as app
    import sentra_engine.agents.coordinator as coord

    class StubAgent:
        async def run(self, _request):
            yield models.EngineEvent(type="step_start")
            yield models.EngineEvent(type="message_delta", content="Hello from ADK engine")
            yield models.EngineEvent(type="message_final", content="Done.")
            yield models.EngineEvent(type="step_end")

    monkeypatch.setattr(coord, "SentraAgent", lambda: StubAgent())
    import sentra_engine.adapters.mongo_session_service as mss

    def _raise(*args, **kwargs):  # pragma: no cover - should not be called
        raise AssertionError("mongo access")

    monkeypatch.setattr(mss, "MongoSessionService", _raise)

    request = models.ConversationRequest(messages=["hello"])

    async def _inner():
        events = []
        async for ev in app.run_conversation(request):
            events.append(ev)
        return events

    events = anyio.run(_inner)

    assert [e.type for e in events] == [
        "step_start",
        "message_delta",
        "message_final",
        "step_end",
    ]
    assert events[1].content == "Hello from ADK engine"
    assert events[2].content == "Done."
    for ev in events:
        assert ev.event_id is not None
        assert ev.timestamp is not None
