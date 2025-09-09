from typing import AsyncGenerator

from sentra.runtime.models import ConversationRequest
from sentra.schemas import Event
from sentra.runtime.tools import DbQueryTool, RagTool
from sentra.runtime.agents.workflows import ParallelAgent


async def run_listings_search_agent(
    request: ConversationRequest, context: dict
) -> AsyncGenerator[Event, None]:
    """Yield a small stream of events for listings search."""
    yield Event(type="step_start", role="system", task_type="listings_search")

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

    yield Event(type="message_delta", role="assistant", content=content)
    yield Event(type="step_end", role="system", task_type="listings_search")
