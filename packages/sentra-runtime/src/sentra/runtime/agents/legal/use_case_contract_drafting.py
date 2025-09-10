from typing import AsyncGenerator

from sentra.runtime.models import ConversationRequest
from sentra.domain.models.event import SentraEvent


async def run_contract_drafting_agent(
    request: ConversationRequest, context: dict
) -> AsyncGenerator[SentraEvent, None]:
    """Yield a small stream of events for contract drafting."""
    yield SentraEvent(type="step_start", task_type="contract_drafting")
    yield SentraEvent(
        type="message_delta",
        content="Here's a draft clause for your contract...",
    )
    yield SentraEvent(type="step_end", task_type="contract_drafting")
