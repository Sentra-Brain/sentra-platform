from typing import AsyncGenerator

from sentra.runtime.models import ConversationRequest
from sentra.domain.models.event import SentraEvent, SentraEventType


async def run_contract_drafting_agent(
    request: ConversationRequest, context: dict, task_run_id: str
) -> AsyncGenerator[SentraEvent, None]:
    """Dummy agent that yields a small stream of events for contract drafting."""

    # Start step
    yield SentraEvent.system_message("Contract drafting started", type=SentraEventType.STEP_START, task_run_id=task_run_id, meta={"step": "contract_drafting"})

    # Streaming delta
    yield SentraEvent.assistant_message("Here's a draft clause for your contract...", type=SentraEventType.MESSAGE_DELTA, task_run_id=task_run_id, meta={"step": "contract_drafting"})

    # End step
    yield SentraEvent.system_message("Contract drafting completed", type=SentraEventType.STEP_END, task_run_id=task_run_id, meta={"step": "contract_drafting"})
