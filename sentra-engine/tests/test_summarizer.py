import pytest

from sentra_engine.agents import update_summary_and_entities


@pytest.mark.anyio("asyncio")
async def test_update_summary_and_entities_returns_summary_and_entities() -> None:
    summary, entities = await update_summary_and_entities("demo", ["hello", "world"])
    assert isinstance(summary, str)
    assert isinstance(entities, dict)
    assert summary  # non-empty
    assert "persons" in entities
