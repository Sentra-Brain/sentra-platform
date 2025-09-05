from typing import AsyncGenerator

from sentra_engine.models import ConversationRequest, EngineEvent
from sentra_engine.tools import DbQueryTool, RagTool
from sentra_engine.agents.workflows import ParallelAgent


async def run_listings_search_agent(
    request: ConversationRequest, context: dict
) -> AsyncGenerator[EngineEvent, None]:
    """Yield a small stream of events for listings search."""
    yield EngineEvent(type="step_start", task_type="listings_search")

    db = DbQueryTool()
    rag = RagTool()
    parallel = ParallelAgent()

    db_task = db.get_listings(city="Madrid", max_budget=1000.0)
    rag_task = rag.retrieve("apartments in Madrid")
    db_results, rag_chunks = await parallel.run_parallel_tasks([db_task, rag_task])

    listings = [] if isinstance(db_results, Exception) else db_results
    rag_text = (
        []
        if isinstance(rag_chunks, Exception)
        else [chunk.content for chunk in rag_chunks]
    )

    parts = []
    if listings:
        parts.append("Here are some listings:\n" + "\n".join(listings))
    if rag_text:
        parts.append("Insights:\n" + "\n".join(rag_text))
    content = "\n\n".join(parts) or "No data found."

    yield EngineEvent(type="message_delta", content=content)
    yield EngineEvent(type="step_end", task_type="listings_search")
