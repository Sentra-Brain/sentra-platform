"""Main public entrypoints for the Sentra engine."""
from __future__ import annotations

from typing import AsyncGenerator

from sentra.runtime.models import ConversationRequest
from sentra.runtime.agents import CoordinatorAgent
from sentra.schemas import Event


async def run_conversation(
    request: ConversationRequest,
) -> AsyncGenerator[Event, None]:
    """Run a conversation with the configured agents.

    This function is the main public entrypoint for consumers of the
    ``sentra-runtime`` package and simply delegates to the
    :class:`CoordinatorAgent`.

    Args:
        request: Incoming conversation request data.

    Yields:
        ``Event`` objects representing the streaming response.
    """

    agent = CoordinatorAgent()
    async for event in agent.run(request):
        yield event
