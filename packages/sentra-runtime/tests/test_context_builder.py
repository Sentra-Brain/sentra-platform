import json
import pytest

from sentra.runtime.context.builder import build_context
from sentra.runtime.models import ConversationRequest
from sentra.runtime.tools.rag_tool import RagChunk, RagTool
from sentra.shared.settings import settings


@pytest.mark.anyio("asyncio")
@pytest.mark.parametrize(
    "token_budget,expected",
    [
        (1, "d"),
        (2, "c\nd"),
        (3, "b\nc\nd"),
    ],
)
async def test_build_context_respects_token_budget(token_budget, expected, monkeypatch) -> None:
    monkeypatch.setattr(settings, "adk_token_budget", token_budget)
    request = ConversationRequest(messages=["a", "b", "c", "d"])
    context = await build_context(request)
    assert context["history"] == expected
    assert context["knowledge"] == ""
    assert "summary" not in context
    assert "entities" not in context


@pytest.mark.anyio("asyncio")
async def test_build_context_adds_summary_and_entities_over_threshold() -> None:
    msgs = [f"m{i}" for i in range(6)]
    request = ConversationRequest(messages=msgs)
    context = await build_context(request)
    assert "summary" in context
    assert "entities" in context
    entities = json.loads(context["entities"])
    assert isinstance(entities, dict)


@pytest.mark.anyio("asyncio")
async def test_build_context_injects_rag_knowledge(monkeypatch) -> None:
    async def fake_retrieve(self, query, *, source_ids=None, document_ids=None, top_k=6):
        return [RagChunk(content="x"), RagChunk(content="x"), RagChunk(content="y")]

    monkeypatch.setattr(RagTool, "retrieve", fake_retrieve)
    request = ConversationRequest(
        messages=["hello"], context_source_ids=["1"], context_document_ids=None
    )
    context = await build_context(request)
    assert context["knowledge"] == "x\ny"


@pytest.mark.anyio("asyncio")
async def test_build_context_skips_rag_when_disabled(monkeypatch) -> None:
    monkeypatch.setattr(settings, "enable_rag", False)

    async def fake_retrieve(self, *args, **kwargs):  # pragma: no cover - should not be called
        raise AssertionError("RAG should be disabled")

    monkeypatch.setattr(RagTool, "retrieve", fake_retrieve)
    request = ConversationRequest(messages=["hello"], context_source_ids=["1"])
    context = await build_context(request)
    assert context["knowledge"] == ""
