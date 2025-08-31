"""Utilities to construct prompt context for agents."""
from __future__ import annotations

from typing import Dict
import json

from sentra_engine.models.conversation import ConversationRequest
from sentra_engine.agents.summarizer import update_summary_and_entities

SUMMARY_THRESHOLD = 5


async def build_context(request: ConversationRequest) -> Dict[str, str]:
    """Build prompt context for a conversation.

    For now the context is extremely small and only includes a short slice of
    conversation history along with a placeholder for knowledge retrieved via
    RAG. When the conversation exceeds ``SUMMARY_THRESHOLD`` turns, the rolling
    summary and entity map are updated as well.

    Args:
        request: Incoming conversation request data.

    Returns:
        A dictionary with ``history`` and ``knowledge`` keys, and optionally
        ``summary`` and ``entities`` when the threshold is met.
    """

    history = "\n".join(request.messages[-3:])
    knowledge = "TODO: injected from RAGTool"
    context: Dict[str, str] = {"history": history, "knowledge": knowledge}

    if len(request.messages) > SUMMARY_THRESHOLD:
        summary, entities = await update_summary_and_entities(
            "demo-id", request.messages
        )
        context["summary"] = summary
        context["entities"] = json.dumps(entities)

    return context
