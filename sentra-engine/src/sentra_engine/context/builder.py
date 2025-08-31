"""Utilities to construct prompt context for agents."""
from __future__ import annotations

from typing import Dict

from sentra_engine.models.conversation import ConversationRequest


def build_context(request: ConversationRequest) -> Dict[str, str]:
    """Build prompt context for a conversation.

    For now the context is extremely small and only includes a short slice of
    conversation history along with a placeholder for knowledge retrieved via
    RAG.

    Args:
        request: Incoming conversation request data.

    Returns:
        A dictionary with ``history`` and ``knowledge`` keys.
    """

    history = "\n".join(request.messages[-3:])
    knowledge = "TODO: injected from RAGTool"
    return {"history": history, "knowledge": knowledge}
