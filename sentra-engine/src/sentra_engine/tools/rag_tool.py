"""Stubbed RAG retrieval tool."""
from __future__ import annotations

from typing import List


class RagTool:
    """Retrieve relevant knowledge chunks from the RAG service."""

    async def retrieve_relevant_chunks(
        self, query: str, source_ids: List[str] | None = None, document_ids: List[str] | None = None
    ) -> str:
        """Return mocked chunks matching the query.

        In the future this will call ``sentra-rag-server`` via HTTP.
        """

        # TODO: integrate with actual RAG service
        return "TODO: retrieved knowledge chunks"
