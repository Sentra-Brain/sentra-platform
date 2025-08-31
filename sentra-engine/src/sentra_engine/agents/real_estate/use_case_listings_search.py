from typing import AsyncGenerator

from sentra_engine.models import ConversationRequest, ConversationEvent


async def run_listings_search_agent(
    request: ConversationRequest, context: dict
) -> AsyncGenerator[ConversationEvent, None]:
    """Yield a small stream of events for listings search."""
    yield ConversationEvent(type="step_start", task_type="listings_search")
    yield ConversationEvent(
        type="message_delta",
        content="I found 3 matching listings in your area...",
    )
    yield ConversationEvent(type="step_end", task_type="listings_search")
