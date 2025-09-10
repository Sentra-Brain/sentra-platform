from typing import AsyncGenerator

from sentra.domain.models.event import SentraEvent, SentraEventType
from sentra.runtime.models import ConversationRequest
from sentra.runtime.tools import DbQueryTool, RagTool
from sentra.runtime.agents.workflows import ParallelAgent


async def run_listings_search_agent(
    request: ConversationRequest, context: dict, task_run_id: str
) -> AsyncGenerator[SentraEvent, None]:
    """Dummy agent that yields a small stream of events for listings search."""

    # Start step
    yield SentraEvent.system_message (
        "Listings search started",
        type=SentraEventType.STEP_START,
        task_run_id=task_run_id,
        meta={"step": "listings_search"},
    )

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

    parts: list[str] = []
    if listings:
        parts.append("Here are some listings:\n" + "\n".join(listings))
    if rag_text:
        parts.append("Insights:\n" + "\n".join(rag_text))

    content = "\n\n".join(parts) or "No data found."

    # Final assistant message
    yield SentraEvent.assistant_message(content, task_run_id=task_run_id)

    # End step
    yield SentraEvent.system_message(
        "Listings search completed",
        type=SentraEventType.STEP_END,
        task_run_id=task_run_id,
        meta={"step": "listings_search"},
    )
