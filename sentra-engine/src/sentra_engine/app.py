"""Main public entrypoints for the Sentra engine."""
from __future__ import annotations

from typing import AsyncGenerator

from sentra_engine.models.conversation import ConversationEvent, ConversationRequest
from sentra_engine.agents import CoordinatorAgent


async def run_conversation(
    request: ConversationRequest,
) -> AsyncGenerator[ConversationEvent, None]:
    """Run a conversation with the configured agents.

    This function is the main public entrypoint for consumers of the
    ``sentra-engine`` package and simply delegates to the
    :class:`CoordinatorAgent`.

    Args:
        request: Incoming conversation request data.

    Yields:
        ``ConversationEvent`` objects representing the streaming response.
    """

    agent = CoordinatorAgent()
    async for event in agent.run(request):
        yield event
