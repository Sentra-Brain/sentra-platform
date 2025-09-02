import pytest

from sentra_engine.config import settings
from sentra_engine.policies.guardrails import (
    PolicyError,
    check_tool_allowed,
    redact_pii,
)
from sentra_engine.tools.rag_tool import RagTool


def test_redact_pii_replaces_name() -> None:
    text = "John went home"
    assert redact_pii(text) == "[REDACTED] went home"


@pytest.mark.anyio("asyncio")
async def test_disallowed_tool_raises_policy_error() -> None:
    with pytest.raises(PolicyError):
        check_tool_allowed("LegalDraftingAgent", "DbQueryTool")


@pytest.mark.anyio("asyncio")
async def test_rag_tool_filters_sources(monkeypatch) -> None:
    monkeypatch.setattr(settings, "use_dummy", True)
    rag = RagTool()
    chunks = await rag.retrieve(
        "query",
        agent_name="LegalDraftingAgent",
        source_ids=["legal-templates", "unknown", "clauses"],
    )
    texts = "\n".join(chunk.content for chunk in chunks)
    assert "(unknown)" not in texts
    assert "(legal-templates)" in texts
    assert "(clauses)" in texts
