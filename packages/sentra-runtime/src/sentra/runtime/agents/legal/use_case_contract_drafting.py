from typing import AsyncGenerator

from sentra.runtime.models import ConversationRequest
from sentra.schemas import Event


async def run_contract_drafting_agent(
    request: ConversationRequest, context: dict
) -> AsyncGenerator[Event, None]:
    """Yield a small stream of events for contract drafting."""
    yield Event(type="step_start", role="system", task_type="contract_drafting")
    yield Event(
        type="message_delta",
        role="assistant",
        content="Here's a draft clause for your contract...",
    )
    yield Event(type="step_end", role="system", task_type="contract_drafting")
