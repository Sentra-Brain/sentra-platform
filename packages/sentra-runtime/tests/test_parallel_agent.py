import time
import anyio

from sentra.runtime.agents.real_estate.use_case_listings_search import run_listings_search_agent
from sentra.runtime.models import ConversationRequest
from sentra.runtime.tools import DbQueryTool, RagTool
from sentra.runtime.tools.rag_tool import RagChunk


def test_listings_search_runs_db_and_rag_in_parallel(monkeypatch):
    async def fake_get_listings(self, city: str, max_budget: float):
        await anyio.sleep(0.2)
        return ["Flat A"]

    async def fake_retrieve(self, query: str, *, agent_name: str = "SentraAgent", source_ids=None, document_ids=None, top_k: int = 6):
        await anyio.sleep(0.2)
        return [RagChunk(content="Insight A")]

    monkeypatch.setattr(DbQueryTool, "get_listings", fake_get_listings)
    monkeypatch.setattr(RagTool, "retrieve", fake_retrieve)

    async def _run():
        req = ConversationRequest(messages=["Find listings"])

        events: list = []
        async for ev in run_listings_search_agent(req, {}):
            events.append(ev)
        return events

    start = time.perf_counter()
    events = anyio.run(_run)
    elapsed = time.perf_counter() - start

    # Each tool sleeps 0.2s; sequential execution would be ~0.4s
    assert elapsed < 0.35

    content = next(e.content for e in events if e.type == "message_delta")
    assert "Flat A" in content
    assert "Insight A" in content
