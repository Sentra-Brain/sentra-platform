from typing import AsyncGenerator

from google.adk.events.event import Event
from google.genai import types
from sentra.runtime.models import ConversationRequest
from sentra.runtime.tools import DbQueryTool, RagTool
from sentra.runtime.agents.workflows import ParallelAgent


async def run_listings_search_agent(
    request: ConversationRequest, context: dict, task_run_id: str
) -> AsyncGenerator[Event, None]:
    """Dummy agent that yields a small stream of events for listings search."""

    # Start step
    yield Event(author="system", content=types.Content(role="system", parts=[types.Part(text="Listings search started")]), custom_metadata={"type": "step_start", "step": "listings_search"})

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
    yield Event(author="assistant", content=types.Content(role="assistant", parts=[types.Part(text=content)]), custom_metadata={"type": "message_final"})

    # End step
    yield Event(author="system", content=types.Content(role="system", parts=[types.Part(text="Listings search completed")]), custom_metadata={"type": "step_end", "step": "listings_search"})
