"""RAG retrieval tool used by the Sentra engine."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

import httpx

from sentra_engine.config import settings
from sentra_engine.policies.guardrails import get_allowed_sources


@dataclass
class RagChunk:
    """A small piece of knowledge returned by the RAG service."""

    content: str
    source_id: Optional[str] = None
    document_id: Optional[str] = None


class RagTool:
    """Retrieve relevant knowledge chunks from the RAG service."""

    async def retrieve(
        self,
        query: str,
        *,
        agent_name: str = "SentraAgent",
        source_ids: List[str] | None = None,
        document_ids: List[str] | None = None,
        top_k: int = 6,
    ) -> List[RagChunk]:
        """Return top ``k`` relevant chunks for ``query``.

        When ``settings.use_dummy`` is enabled a deterministic mock response is
        produced. Otherwise this method attempts an HTTP call to the future
        ``sentra-rag-server`` endpoint. Any network failure results in an empty
        list so that the engine degrades gracefully.
        """

        allowed_sources = get_allowed_sources(agent_name)
        if source_ids and "*" not in allowed_sources:
            source_ids = [s for s in source_ids if s in allowed_sources]

        if settings.use_dummy:
            seeds = source_ids or document_ids or ["mock"]
            chunks = [
                RagChunk(content=f"[{i}] {query} ({sid})")
                for i, sid in enumerate(seeds[:top_k], start=1)
            ]
            while len(chunks) < top_k:
                idx = len(chunks) + 1
                chunks.append(RagChunk(content=f"[{idx}] {query}"))
            return chunks

        payload = {
            "query": query,
            "source_ids": source_ids,
            "document_ids": document_ids,
            "top_k": top_k,
        }

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    "http://sentra-rag-server/retrieve", json=payload, timeout=30
                )
                resp.raise_for_status()
                data = resp.json()
        except Exception:
            return []

        items = data.get("chunks", data)
        return [RagChunk(content=item["content"]) for item in items if "content" in item]
