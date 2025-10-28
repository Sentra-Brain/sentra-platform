from __future__ import annotations

import json
from typing import Any, Sequence
import httpx
from agent_framework import (
    ContextProvider,
    Context,
    ChatMessage,
    ChatOptions,
    ChatClientProtocol,
)
from sentra.shared.settings import settings
from sentra.shared.logging import get_logger

logger = get_logger(__name__)


class RagContextProvider(ContextProvider):
    """
    ContextProvider that integrates Sentra's rag-server.

    Responsibilities:
    - Before each agent invocation (`invoking`):
        retrieves top-K relevant memories from rag-server
        and injects them as additional context/instructions.
    - After each invocation (`invoked`):
        stores the assistant's final messages back to rag-server
        for long-term memory.
    """

    def __init__(
        self,
        chat_client: ChatClientProtocol,
        user_id: str,
        rag_server_url: str | None = None,
        top_k: int = 5,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self._chat_client = chat_client
        self.user_id = user_id
        self.top_k = top_k
        self.base_url = (rag_server_url or settings.rag_server_url).rstrip("/")
        self._memories: list[str] = []

    async def invoking(
        self,
        messages: ChatMessage | Sequence[ChatMessage],
        **kwargs: Any,
    ) -> Context:
        """Fetch top-K relevant memories and add them as extra instructions."""
        query = None
        if isinstance(messages, Sequence) and messages:
            # Use the latest user message text as query
            last_user = next(
                (m for m in reversed(messages) if getattr(m.role, "value", "") == "user"),
                None,
            )
            query = last_user.text if last_user and last_user.text else None

        if not query:
            return Context()  # nothing to add

        try:
            async with httpx.AsyncClient() as client:
                payload = {"user_id": self.user_id, "query": query, "limit": self.top_k}
                resp = await client.post(f"{self.base_url}/search_memories", json=payload, timeout=15.0)
                resp.raise_for_status()
                data = resp.json().get("results", [])
        except Exception as exc:
            logger.warning(f"[RAG] search_memories failed: {exc}")
            data = []

        if not data:
            return Context()

        # Build combined instruction text
        context_text = "\n".join(
            f"- {item.get('text')}" for item in data if item.get("text")
        )
        self._memories = [item.get("text") for item in data if item.get("text")]

        return Context(instructions=f"Relevant background facts:\n{context_text}")

    async def invoked(
        self,
        request_messages: ChatMessage | Sequence[ChatMessage],
        response_messages: ChatMessage | Sequence[ChatMessage] | None = None,
        invoke_exception: Exception | None = None,
        **kwargs: Any,
    ) -> None:
        """Send assistant final messages to rag-server for memorization."""
        if not response_messages:
            return

        # Flatten in case it's a single ChatMessage
        responses = (
            [response_messages]
            if isinstance(response_messages, ChatMessage)
            else list(response_messages)
        )

        async with httpx.AsyncClient() as client:
            for msg in responses:
                try:
                    if getattr(msg.role, "value", "") != "assistant":
                        continue
                    text = msg.text.strip() if msg.text else None
                    if not text:
                        continue
                    payload = {
                        "user_id": self.user_id,
                        "text": text,
                    }
                    await client.post(f"{self.base_url}/memorize", json=payload, timeout=10.0)
                except Exception as exc:
                    logger.warning(f"[RAG] memorize failed: {exc}")

    def serialize(self) -> str:
        """Serialize current state (e.g. last retrieved memories)."""
        return json.dumps({"memories": self._memories, "top_k": self.top_k})

    @classmethod
    def deserialize(cls, chat_client: ChatClientProtocol, state: str, **kwargs: Any):
        """Rebuild provider from serialized JSON state."""
        data = json.loads(state)
        instance = cls(chat_client=chat_client, **kwargs)
        instance._memories = data.get("memories", [])
        instance.top_k = data.get("top_k", 5)
        return instance
