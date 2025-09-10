"""Main public entrypoints for the Sentra engine."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import AsyncGenerator
from uuid import uuid4

from sentra.domain.models.event import SentraEvent
from sentra.runtime.models.conversation import ConversationRequest
from sentra.runtime.agents import CoordinatorAgent


async def run_conversation(
    request: ConversationRequest,
) -> AsyncGenerator[SentraEvent, None]:
    """Run a conversation with the configured agents.

    This function is the main public entrypoint for consumers of the
    ``sentra-runtime`` package and simply delegates to the
    :class:`CoordinatorAgent`.

    Args:
        request: Incoming conversation request data.

    Yields:
        ``SentraEvent`` objects representing the streaming response.
    """

    agent = CoordinatorAgent()
    async for event in agent.run(request):
        if event.event_id is None:
            event.event_id = uuid4().hex
        if event.timestamp is None:
            event.timestamp = datetime.now(timezone.utc)
        yield event
