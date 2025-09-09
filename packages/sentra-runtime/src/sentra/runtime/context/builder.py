"""Utilities to construct prompt context for agents."""
from __future__ import annotations

from typing import Dict
import json

from sentra.runtime.adapters.rag_memory_service import RagMemoryService
from sentra.runtime.models.conversation import ConversationRequest
from sentra.runtime.agents.summarizer import update_summary_and_entities
from sentra.runtime.tools.rag_tool import RagTool
from sentra.shared.settings import settings

SUMMARY_THRESHOLD = 5

memory_service = RagMemoryService()


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

    max_messages = max(1, settings.adk_token_budget)
    history = "\n".join(request.messages[-max_messages:])
    knowledge = ""

    if settings.enable_rag and (request.context_source_ids or request.context_document_ids):
        rag_tool = RagTool()
        chunks = await rag_tool.retrieve(
            request.messages[-1] if request.messages else "",
            source_ids=request.context_source_ids,
            document_ids=request.context_document_ids,
        )
        seen: set[str] = set()
        deduped = []
        for chunk in chunks:
            if chunk.content not in seen:
                seen.add(chunk.content)
                deduped.append(chunk.content)
        knowledge = "\n".join(deduped)

    memories = ""
    if request.user_id and request.messages:
        results = await memory_service.search_memory(
            request.user_id, request.messages[-1]
        )
        seen_mem: set[str] = set()
        deduped_mem: list[str] = []
        for res in results:
            content = res.get("content")
            if content and content not in seen_mem:
                seen_mem.add(content)
                deduped_mem.append(content)
        memories = "\n".join(deduped_mem)

    context: Dict[str, str] = {"history": history, "knowledge": knowledge, "memories": memories}

    if len(request.messages) > SUMMARY_THRESHOLD:
        summary, entities = await update_summary_and_entities(
            "demo-id", request.messages
        )
        context["summary"] = summary
        context["entities"] = json.dumps(entities)

    return context
