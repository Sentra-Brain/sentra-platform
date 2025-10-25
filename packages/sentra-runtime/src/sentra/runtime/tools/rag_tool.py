"""RAG retrieval tool used by the Sentra runtime (MAF-compatible)."""

from typing import Annotated, List, Optional
import httpx
import logging
from agent_framework import ai_function

from sentra.runtime.config import settings
from sentra.runtime.policies.guardrails import get_allowed_sources
from sentra.runtime.policies import retry_with_backoff


@ai_function(
    name="rag_search_tool",
    description="Retrieve top relevant knowledge chunks from Sentra's RAG service."
)
async def rag_search_tool(
    query: Annotated[str, "Natural language query to search within the knowledge base."],
    agent_name: Annotated[str, "Name of the invoking agent."] = "sentra_agent",
    source_ids: Annotated[Optional[List[str]], "Restrict retrieval to these source IDs."] = None,
    document_ids: Annotated[Optional[List[str]], "Restrict retrieval to these document IDs."] = None,
    top_k: Annotated[int, "Number of results to return."] = 6,
) -> List[str]:
    """Retrieve relevant chunks of knowledge from the RAG server."""
    allowed_sources = get_allowed_sources(agent_name)
    if source_ids and "*" not in allowed_sources:
        source_ids = [s for s in source_ids if s in allowed_sources]

    if settings.use_dummy:
        seeds = source_ids or document_ids or ["mock"]
        return [f"[{i}] {query} ({sid})" for i, sid in enumerate(seeds[:top_k], start=1)]

    payload = {
        "query": query,
        "source_ids": source_ids,
        "document_ids": document_ids,
        "top_k": top_k,
    }

    async def _call() -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{settings.rag_server_url.rstrip('/')}/retrieve", json=payload, timeout=30
            )
            resp.raise_for_status()
            return resp.json()

    data = await retry_with_backoff(
        _call,
        logger=logging.getLogger(__name__),
        label="rag.retrieve",
    )
    if not data:
        return []

    items = data.get("chunks", data)
    return [item["content"] for item in items if "content" in item]
