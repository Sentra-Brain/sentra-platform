# packages/sentra-runtime/src/sentra/runtime/adapters/mongo_chat_message_store.py
from datetime import datetime, timezone
from agent_framework import ChatMessage, ChatMessageStore
from sentra.infra.nosql.conversation_mongo_repository import get_conversation_mongo_repository
from sentra.shared.logging import get_logger

logger = get_logger(__name__)


class MongoChatMessageStore(ChatMessageStore):
    """MAF-compatible ChatMessageStore backed by MongoConversationRepository."""

    def __init__(self, conversation_id, user_id):
        self.repo = get_conversation_mongo_repository()
        self.conversation_id = conversation_id
        self.user_id = user_id

    async def add_messages(self, messages: list[ChatMessage]):
        """Append one or more ChatMessages to the Mongo conversation document."""
        for msg in messages:
            try:
                # Full serialized representation (for exact reconstruction)
                data = msg.to_dict(exclude=ChatMessage.DEFAULT_EXCLUDE)

                # lightweight _view projection for quick UI retrieval
                role_value = getattr(getattr(msg, "role", None), "value", None) or "unknown"
                view = {
                    "role": role_value,
                    "text": msg.text.strip() if msg.text else None,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }

                # Store both full message and its simplified projection
                data["_view"] = view

                await self.repo.append_message(
                    conversation_id=self.conversation_id,
                    user_id=self.user_id,
                    message=data,
                )

            except Exception as exc:
                logger.warning(f"Failed to store chat message: {exc}")

    async def list_messages(self) -> list[ChatMessage]:
        """Return all ChatMessages for this conversation."""
        try:
            doc = await self.repo.get_conversation_by_id(self.conversation_id, self.user_id)
        except Exception as exc:
            logger.warning(f"Conversation fetch failed: {exc}")
            return []

        raw_messages = doc.get("messages", [])
        messages: list[ChatMessage] = []

        for raw in raw_messages:
            try:
                if isinstance(raw, str):
                    import json
                    raw = json.loads(raw)
                messages.append(ChatMessage.from_dict(raw))
            except Exception as exc:
                logger.warning(f"Failed to restore ChatMessage: {exc}")
        return messages

    async def serialize_state(self, **_):
        """Serialize minimal store state for inclusion in AgentThread state."""
        return {
            "conversation_id": self.conversation_id,
            "user_id": self.user_id,
        }

    async def deserialize_state(self, state, **_):
        """Restore store state when a thread is resumed."""
        self.conversation_id = state.get("conversation_id")
        self.user_id = state.get("user_id")
