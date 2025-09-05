import anyio
import importlib


def test_run_conversation_streams_dummy_events(monkeypatch):
    monkeypatch.setenv("USE_DUMMY", "true")

    # Reload modules so that configuration picks up the env var
    import sentra.runtime.config as cfg
    importlib.reload(cfg)
    import sentra.runtime.models as models
    importlib.reload(models)
    import sentra.runtime.agents.coordinator as coord
    importlib.reload(coord)
    import sentra.runtime.app as app
    importlib.reload(app)

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
