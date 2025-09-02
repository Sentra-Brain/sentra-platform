import types
import uuid
import sys

from pydantic import BaseModel

from sentra_brain_api.settings import EngineMode, settings
from sentra_brain_api.crosscutting.authorization import get_authenticated_user


def _payload() -> dict[str, str]:
    return {
        "user_id": str(uuid.uuid4()),
        "conversation_id": str(uuid.uuid4()),
        "content": "hi",
    }


def _override_auth(client):
    fake_user = types.SimpleNamespace(id=uuid.uuid4())
    client.app.dependency_overrides[get_authenticated_user] = lambda: fake_user


def test_adk_engine_selected(client, monkeypatch):
    monkeypatch.setattr(settings, "engine_mode", EngineMode.ADK)

    called = []

    async def fake_run(_request):
        called.append(True)
        yield {"type": "message_final", "content": "ok"}

    monkeypatch.setattr("sentra_engine.run_conversation", fake_run, raising=False)

    class DummyReq(BaseModel):
        messages: list[str] = []
        context_source_ids: list[str] | None = None
        context_document_ids: list[str] | None = None

    monkeypatch.setitem(sys.modules, "sentra_engine.models", types.SimpleNamespace(ConversationRequest=DummyReq))

    # If the legacy engine is instantiated in ADK mode, the test will
    # still pass but the call counter below ensures the ADK path was used.

    _override_auth(client)
    resp = client.post("/chat/send", json=_payload())
    assert resp.status_code == 200
    assert called, "ADK run_conversation was not invoked"


def test_legacy_engine_selected(client, monkeypatch):
    monkeypatch.setattr(settings, "engine_mode", EngineMode.LEGACY)

    called = []

    class FakeEngine:
        async def run_fast(self, **_):  # type: ignore[no-untyped-def]
            called.append(True)
            yield {"type": "message_final", "content": "ok"}

    monkeypatch.setattr(
        "sentra_brain_api.features.chat.controller.ConversationEngine",
        lambda *_, **__: FakeEngine(),
    )

    import sentra_engine as legacy_engine

    def fail_run(*_, **__):  # pragma: no cover
        raise AssertionError("ADK engine should not be called")

    monkeypatch.setattr(legacy_engine, "run_conversation", fail_run, raising=False)

    _override_auth(client)
    resp = client.post("/chat/send", json=_payload())
    assert resp.status_code == 200
    assert called, "Legacy engine run_fast was not invoked"

