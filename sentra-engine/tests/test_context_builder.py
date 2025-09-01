import json
import pytest

from sentra_engine.context import build_context
from sentra_engine.models import ConversationRequest
from sentra_engine.tools.rag_tool import RagChunk, RagTool


@pytest.mark.anyio("asyncio")
async def test_build_context_returns_last_three_messages() -> None:
    request = ConversationRequest(messages=["a", "b", "c", "d"])
    context = await build_context(request)
    assert context["history"] == "b\nc\nd"
    assert context["knowledge"] == "TODO: injected from RAGTool"
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
