"""Utilities to construct prompt context for agents."""
from __future__ import annotations

from typing import Dict

from sentra_engine.models.conversation import ConversationRequest


def build_context(request: ConversationRequest) -> Dict[str, str]:
    """Build a placeholder prompt context for a conversation.

    Args:
        request: Incoming conversation request data.

    Returns:
        A dictionary representing prompt context. Currently empty.
    """
    # TODO: implement real context construction logic
    return {}
