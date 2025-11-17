from __future__ import annotations

from agent_framework import ChatMessage, ChatMessageStore
from agent_framework._threads import ChatMessageStoreProtocol, ChatMessageStoreState
from typing import Sequence, Any, MutableMapping

from sentra.runtime.adapters.thread_cache import InMemoryThreadCache
from sentra.infra.nosql.conversation_mongo_repository import get_conversation_mongo_repository
from sentra.shared.logging import get_logger

logger = get_logger(__name__)


class ChatMessageStoreHybrid(ChatMessageStoreProtocol):
    """
    A fully compliant message store for Microsoft Agent Framework.

    Responsibilities:
      ✓ Persist ALL messages immediately to Mongo
      ✓ Restore ALL messages on next invocation
      ✓ Persist/restore thread state (RAG memory, internal reasoning traces)
      ✓ Provide in-memory caching to reduce Mongo load

    """

    _thread_cache = InMemoryThreadCache(capacity=512)

    def __init__(self, conversation_id: str, user_id: str):
        self.conversation_id = conversation_id
        self.user_id = user_id
        self.repo = get_conversation_mongo_repository()

    # ----------------------------------------------------------------------
    # 1. STORE MESSAGES  (called on EVERY update: user, assistant, tool)
    # ----------------------------------------------------------------------
    async def add_messages(self, messages: Sequence[ChatMessage]) -> None:
        """Persist all messages in chronological order to MongoDB."""
        for msg in messages:
            try:
                self.repo.append_message(
                    self.conversation_id,
                    self.user_id,
                    msg.to_dict()
                )
            except Exception as exc:
                logger.warning(f"[HybridStore] add_messages failed: {exc}")

    # ----------------------------------------------------------------------
    # 2. LOAD ALL MESSAGES FOR NEXT RUN (context)
    # ----------------------------------------------------------------------
    async def list_messages(self) -> list[ChatMessage]:
        doc = self.repo.get_conversation_by_id(self.conversation_id, self.user_id)
        if not doc:
            return []
        raw = doc.get("messages", [])
        return [ChatMessage.from_dict(m) for m in raw]

    # ----------------------------------------------------------------------
    # 3. THREAD STATE RESTORE  (MAF internal context)
    # ----------------------------------------------------------------------
    async def load_thread_state(self) -> dict | None:
        key = f"{self.user_id}:{self.conversation_id}"

        cached = await self._thread_cache.get(key)
        if cached:
            return cached

        try:
            state = self.repo.load_thread_state(self.conversation_id, self.user_id)
            if state:
                await self._thread_cache.set(key, state)
            return state
        except Exception as exc:
            logger.warning(f"[HybridStore] load_thread_state failed: {exc}")
            return None

    # ----------------------------------------------------------------------
    # 4. THREAD STATE SAVE (MAF internal thread serialization)
    # ----------------------------------------------------------------------
    async def save_thread_state(self, state: dict):
        key = f"{self.user_id}:{self.conversation_id}"

        await self._thread_cache.set(key, state)

        try:
            self.repo.save_thread_state(self.conversation_id, self.user_id, state)
        except Exception as exc:
            logger.warning(f"[HybridStore] save_thread_state failed: {exc}")

    # ----------------------------------------------------------------------
    # 5. SERIALIZATION API FOR AGENT FRAMEWORK (required by protocol)
    # ----------------------------------------------------------------------
    async def serialize(self, **kwargs: Any) -> dict[str, Any]:
        """
        Used when the thread itself wants to serialize the store.
        We simply serialize the messages as the framework requires.
        """
        messages = await self.list_messages()
        state = ChatMessageStoreState(messages=messages)
        return state.to_dict()

    @classmethod
    async def deserialize(
        cls,
        serialized_store_state: MutableMapping[str, Any],
        **kwargs: Any,
    ) -> "ChatMessageStoreHybrid":
        """
        Framework entrypoint to rebuild a store from serialization.

        In our case, thread restore already happens through our own Mongo load,
        so deserialize() simply returns an empty shell – the agent will call list_messages().
        """
        conversation_id = kwargs.get("conversation_id")
        user_id = kwargs.get("user_id")

        instance = cls(conversation_id=conversation_id, user_id=user_id)

        # If serialized messages exist (rare), restore them.
        if serialized_store_state and "messages" in serialized_store_state:
            for msg_dict in serialized_store_state["messages"]:
                try:
                    instance.repo.append_message(
                        conversation_id, user_id, msg_dict
                    )
                except Exception as exc:
                    logger.warning(f"[HybridStore] deserialize failed: {exc}")

        return instance

    async def update_from_state(
        self,
        serialized_store_state: MutableMapping[str, Any],
        **kwargs: Any,
    ) -> None:
        """
        Called when the thread state is updated without full reconstruction.
        In practice: extremely rare.

        We simply append any new messages that appear.
        """
        if not serialized_store_state:
            return

        try:
            state = ChatMessageStoreState.from_dict(serialized_store_state)
            for msg in state.messages:
                self.repo.append_message(
                    self.conversation_id,
                    self.user_id,
                    msg.to_dict(),
                )
        except Exception as exc:
            logger.warning(f"[HybridStore] update_from_state failed: {exc}")
