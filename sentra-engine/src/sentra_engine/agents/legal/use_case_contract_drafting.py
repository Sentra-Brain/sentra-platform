from typing import AsyncGenerator

from sentra_engine.models import ConversationRequest, ConversationEvent


async def run_contract_drafting_agent(
    request: ConversationRequest, context: dict
) -> AsyncGenerator[ConversationEvent, None]:
    """Yield a small stream of events for contract drafting."""
    yield ConversationEvent(type="step_start", task_type="contract_drafting")
    yield ConversationEvent(
        type="message_delta",
        content="Here's a draft clause for your contract...",
    )
    yield ConversationEvent(type="step_end", task_type="contract_drafting")
