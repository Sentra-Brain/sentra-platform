from agent_framework import ChatMessage, ChatMessageStore
from sentra.runtime.adapters.thread_cache import InMemoryThreadCache
from sentra.infra.nosql.conversation_mongo_repository import get_conversation_mongo_repository
from sentra.shared.logging import get_logger

logger = get_logger(__name__)

class ChatMessageStoreHybrid(ChatMessageStore):
    """Hybrid store that merges in-memory cache and Mongo persistence."""

    _thread_cache = InMemoryThreadCache(capacity=256)

    def __init__(self, conversation_id: str, user_id: str):
        super().__init__()
        self.conversation_id = conversation_id
        self.user_id = user_id
        self.repo = get_conversation_mongo_repository()

    # --- Chat messages ---
    async def add_messages(self, messages: list[ChatMessage]):
        from datetime import datetime, timezone
        for msg in messages:
            data = msg.to_dict()
            data["_view"] = {
                "role": getattr(msg.role, "value", None),
                "text": msg.text,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            try:
                self.repo.append_message(self.conversation_id, self.user_id, data)
            except Exception as exc:
                logger.warning(f"[HybridStore] Failed to append message: {exc}")

    async def list_messages(self) -> list[ChatMessage]:
        doc = self.repo.get_conversation_by_id(self.conversation_id, self.user_id)
        if not doc:
            return []
        raw = doc.get("messages", [])
        from agent_framework import ChatMessage
        return [ChatMessage.from_dict(m) for m in raw]

    # --- Thread state ---
    async def load_thread_state(self) -> dict | None:
        """Try cache first, then Mongo."""
        key = f"{self.user_id}:{self.conversation_id}"
        cached = await self._thread_cache.get(key)
        if cached:
            return cached
        state = self.repo.load_thread_state(self.conversation_id, self.user_id)
        if state:
            await self._thread_cache.set(key, state)
        return state

    async def save_thread_state(self, state: dict):
        key = f"{self.user_id}:{self.conversation_id}"
        await self._thread_cache.set(key, state)
        try:
            self.repo.save_thread_state(self.conversation_id, self.user_id, state)
        except Exception as exc:
            logger.warning(f"[HybridStore] Failed to persist thread state: {exc}")
