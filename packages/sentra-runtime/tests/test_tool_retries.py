import logging
import asyncio
import httpx
import pytest

from sentra.runtime.config import settings
from sentra.runtime.tools import RagTool, DbQueryTool


@pytest.mark.anyio
async def test_rag_tool_retries_until_success(monkeypatch, caplog) -> None:
    settings.use_dummy = False
    attempts = {"n": 0}

    class FailingClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *exc):
            return False

        async def post(self, *args, **kwargs):
            attempts["n"] += 1
            if attempts["n"] < 3:
                raise httpx.TransportError("boom")

            class Resp:
                def raise_for_status(self):
                    return None

                def json(self):
                    return {"chunks": [{"content": "ok"}]}

            return Resp()

    async def no_sleep(_):
        return None

    monkeypatch.setattr("asyncio.sleep", no_sleep)
    monkeypatch.setattr(
        "sentra.runtime.tools.rag_tool.httpx.AsyncClient", FailingClient
    )

    tool = RagTool()
    with caplog.at_level(logging.INFO, logger="sentra.runtime.telemetry"):
        chunks = await tool.retrieve("hello")

    assert [c.content for c in chunks] == ["ok"]
    assert attempts["n"] == 3
    contents = [rec.__dict__.get("content") for rec in caplog.records if rec.msg == "event"]
    assert "rag.retrieve failed (attempt 1/3)" in contents
    assert "rag.retrieve failed (attempt 2/3)" in contents


@pytest.mark.anyio
async def test_db_tool_retries_and_fallback_event(monkeypatch, caplog) -> None:
    tool = DbQueryTool()
    attempts = {"n": 0}

    async def failing_fetch(self, limit):
        attempts["n"] += 1
        raise RuntimeError("db down")

    async def no_sleep(_):
        return None

    monkeypatch.setattr(DbQueryTool, "_fetch_property_summaries", failing_fetch)
    monkeypatch.setattr("asyncio.sleep", no_sleep)

    with caplog.at_level(logging.INFO, logger="sentra.runtime.telemetry"):
        result = await tool.get_property_summaries()

    assert result == ""
    assert attempts["n"] == 3
    contents = [rec.__dict__.get("content") for rec in caplog.records if rec.msg == "event"]
    assert any("failed after 3 attempts" in c for c in contents)
