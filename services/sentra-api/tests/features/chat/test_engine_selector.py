import types
import uuid
import sys

import sys
import types
import uuid

from pydantic import BaseModel

from sentra_core.settings import EngineMode, settings
from sentra_brain_api.crosscutting.authorization import get_authenticated_user


def _payload() -> dict[str, str]:
    sid = uuid.uuid4()
    return {
        "user_id": str(uuid.uuid4()),
        "session_id": str(sid),
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

    stub_engine = types.SimpleNamespace(run_conversation=fake_run)
    monkeypatch.setitem(sys.modules, "sentra_engine", stub_engine)

    class DummyReq(BaseModel):
        messages: list[str] = []
        context_source_ids: list[str] | None = None
        context_document_ids: list[str] | None = None

    monkeypatch.setitem(sys.modules, "sentra_engine.models", types.SimpleNamespace(ConversationRequest=DummyReq))

    # If the legacy engine is instantiated in ADK mode, the test will
    # still pass but the call counter below ensures the ADK path was used.

    _override_auth(client)
    payload = _payload()
    resp = client.post(f"/sessions/{payload['session_id']}/messages", json=payload)
    assert resp.status_code == 200
    assert called, "ADK run_conversation was not invoked"


def test_legacy_engine_selected(client, monkeypatch):
    monkeypatch.setattr(settings, "engine_mode", EngineMode.LEGACY)

    called = []

    class FakeEngine:
        async def run_fast(self, **_):  # type: ignore[no-untyped-def]
            called.append(True)
            yield {"type": "message_final", "content": "ok"}

    stub_root = types.ModuleType("sentra_engine")
    sys.modules["sentra_engine"] = stub_root
    sys.modules["sentra_engine.conversation"] = types.ModuleType(
        "sentra_engine.conversation"
    )
    sys.modules["sentra_engine.conversation.entrypoint"] = types.ModuleType(
        "sentra_engine.conversation.entrypoint"
    )
    sys.modules[
        "sentra_engine.conversation.entrypoint.conversation_engine"
    ] = types.SimpleNamespace(ConversationEngine=lambda *_, **__: FakeEngine())

    def fail_run(*_, **__):  # pragma: no cover
        raise AssertionError("ADK engine should not be called")
    stub_root.run_conversation = fail_run

    _override_auth(client)
    payload = _payload()
    resp = client.post(f"/sessions/{payload['session_id']}/messages", json=payload)
    assert resp.status_code == 200
    assert called, "Legacy engine run_fast was not invoked"

