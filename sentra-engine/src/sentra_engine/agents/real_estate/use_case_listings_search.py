from typing import AsyncGenerator

from sentra_engine.models import ConversationRequest, ConversationEvent
from sentra_engine.tools import DbQueryTool


async def run_listings_search_agent(
    request: ConversationRequest, context: dict
) -> AsyncGenerator[ConversationEvent, None]:
    """Yield a small stream of events for listings search."""
    yield ConversationEvent(type="step_start", task_type="listings_search")
    db = DbQueryTool()
    results = await db.get_listings(city="Madrid", max_budget=1000.0)
    content = "Here are some listings:\n" + "\n".join(results)
    yield ConversationEvent(type="message_delta", content=content)
    yield ConversationEvent(type="step_end", task_type="listings_search")
