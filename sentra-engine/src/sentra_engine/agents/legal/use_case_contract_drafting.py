from typing import AsyncGenerator

from sentra_engine.models import ConversationRequest, EngineEvent


async def run_contract_drafting_agent(
    request: ConversationRequest, context: dict
) -> AsyncGenerator[EngineEvent, None]:
    """Yield a small stream of events for contract drafting."""
    yield EngineEvent(type="step_start", task_type="contract_drafting")
    yield EngineEvent(
        type="message_delta",
        content="Here's a draft clause for your contract...",
    )
    yield EngineEvent(type="step_end", task_type="contract_drafting")
