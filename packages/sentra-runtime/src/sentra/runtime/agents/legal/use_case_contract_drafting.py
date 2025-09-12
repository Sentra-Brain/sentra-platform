from typing import AsyncGenerator

from sentra.runtime.models import ConversationRequest
from google.adk.events.event import Event
from google.genai import types


async def run_contract_drafting_agent(
    request: ConversationRequest, context: dict, task_run_id: str
) -> AsyncGenerator[Event, None]:
    """Dummy agent that yields a small stream of events for contract drafting."""

    # Start step
    yield Event(author="system", content=types.Content(role="system", parts=[types.Part(text="Contract drafting started")]), custom_metadata={"type": "step_start", "step": "contract_drafting"})

    # Streaming delta
    yield Event(author="assistant", content=types.Content(role="assistant", parts=[types.Part(text="Here's a draft clause for your contract...")]), custom_metadata={"type": "message_delta", "step": "contract_drafting"})

    # End step
    yield Event(author="system", content=types.Content(role="system", parts=[types.Part(text="Contract drafting completed")]), custom_metadata={"type": "step_end", "step": "contract_drafting"})
