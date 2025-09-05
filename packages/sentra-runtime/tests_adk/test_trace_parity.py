import json
from pathlib import Path
import anyio
from sentra.runtime.app import run_conversation
from sentra.runtime.models import ConversationRequest

FIXTURES = Path(__file__).parent / "fixtures"


def _load_fixture(name: str):
    with open(FIXTURES / name, "r", encoding="utf-8") as f:
        return json.load(f)


def _run_adk(prompt: str):
    async def _inner():
        req = ConversationRequest(messages=[prompt])
        events = []
        async for ev in run_conversation(req):
            events.append(ev.model_dump())
        return events

    return anyio.run(_inner)


def assert_trace_equivalent(actual, expected, text_tol: int = 20):
    assert len(actual) == len(expected)
    for a, e in zip(actual, expected):
        assert a.get("type") == e.get("type")
        assert a.get("task_type") == e.get("task_type")
        if e.get("content"):
            a_tokens = len((a.get("content") or "").split())
            e_tokens = len((e.get("content") or "").split())
            assert abs(a_tokens - e_tokens) <= text_tol
        if e.get("chunks") is not None:
            assert len(a.get("chunks", [])) == len(e.get("chunks", []))


def test_contract_drafting_parity():
    expected = _load_fixture("contract_draft_legacy.json")
    actual = _run_adk("Can you draft this contract?")
    assert_trace_equivalent(actual, expected)


def test_listings_search_parity():
    expected = _load_fixture("listings_search_legacy.json")
    actual = _run_adk("Show apartment listings in Madrid")
    assert_trace_equivalent(actual, expected)
