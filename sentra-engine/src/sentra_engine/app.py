"""Main public entrypoints for the Sentra engine."""
from __future__ import annotations

from sentra_engine.models.conversation import ConversationEvent, ConversationRequest


async def run_conversation(request: ConversationRequest) -> ConversationEvent:
    """Run a conversation with the configured agents.

    This function is the main public entrypoint for consumers of the
    ``sentra-engine`` package.

    Args:
        request: Incoming conversation request data.

    Returns:
        A placeholder conversation event.
    """
    # TODO: orchestrate conversation between agents
    return ConversationEvent(message="")
