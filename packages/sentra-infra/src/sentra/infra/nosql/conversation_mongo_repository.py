# packages/sentra-infra/src/sentra/infra/nosql/repositories/conversation_mongo_repository.py
from datetime import datetime, timezone
from functools import lru_cache
from uuid import UUID
from pymongo import MongoClient
from sentra.domain.repository.conversation_repository import IConversationNoSQLRepository
from sentra.infra.nosql.mongo_settings import settings
from sentra.shared.logging import get_logger

logger = get_logger("sentra.infra.nosql.repositories.conversation_mongo_repository")


class ConversationMongoRepository(IConversationNoSQLRepository):
    """MongoDB implementation for runtime conversation persistence (messages, metadata mirror)."""

    def __init__(self):
        self.client = MongoClient(
            settings.mongo_url,
            uuidRepresentation="standard",
        )
        self.db = self.client[settings.mongo_database]
        self._ensure_indexes()

        logger.info(
            f"[Mongo] Connected to database {settings.mongo_database} "
            f"at {settings.mongo_host}:{settings.mongo_port}"
        )

    # -------------------------------------------------------------------------
    # Initialization
    # -------------------------------------------------------------------------
    def _ensure_indexes(self):
        coll = self.db["conversations"]
        coll.create_index([("user_id", 1), ("_id", 1)], name="by_user_and_id")

    # -------------------------------------------------------------------------
    # Collection access
    # -------------------------------------------------------------------------
    def _coll(self):
        return self.db["conversations"]

    # -------------------------------------------------------------------------
    # CRUD
    # -------------------------------------------------------------------------
    def create_conversation(self, conversation_id: UUID, user_id: UUID, **fields) -> dict:
        """Create a new conversation document."""
        doc = {
            "_id": str(conversation_id),
            "user_id": str(user_id),
            "created_at": datetime.now(timezone.utc),
            "messages": [],
            "metadata": {},
            **{k: v for k, v in fields.items() if v is not None and k != "initial_prompt"},
        }

        self._coll().insert_one(doc)
        logger.debug(f"[Mongo] Created conversation {conversation_id} for user {user_id}")
        return doc

    def get_conversation_by_id(self, conversation_id: UUID, user_id: UUID) -> dict | None:
        """Retrieve a conversation document."""
        doc = self._coll().find_one({"_id": str(conversation_id), "user_id": str(user_id)})
        if not doc:
            logger.warning(
                f"[Mongo] Conversation not found with ID {conversation_id} for user {user_id}"
            )
            return None
        return doc

    def update_conversation(self, conversation_id: UUID, updates: dict) -> int:
        """Update top-level fields of a conversation document."""
        result = self._coll().update_one({"_id": str(conversation_id)}, {"$set": updates})
        if result.modified_count == 0:
            logger.warning(f"[Mongo] No conversation updated: {conversation_id}")
        return result.modified_count

    def delete_conversation(self, conversation_id: UUID, user_id: UUID) -> None:
        """Delete a conversation document."""
        self._coll().delete_one({"_id": str(conversation_id), "user_id": str(user_id)})

    # -------------------------------------------------------------------------
    # Helpers / extensions
    # -------------------------------------------------------------------------
    def _stringify_uuids(self, obj):
        """Recursively convert UUIDs to strings for Mongo serialization."""
        if isinstance(obj, UUID):
            return str(obj)
        if isinstance(obj, dict):
            return {k: self._stringify_uuids(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [self._stringify_uuids(v) for v in obj]
        return obj

    def append_message(self, conversation_id: UUID, user_id: UUID | None, message: dict) -> int:
        """Append a message to the conversation (MAF ChatMessageStore compatible)."""
        safe_message = self._stringify_uuids(message)
        result = self._coll().update_one(
            {"_id": str(conversation_id), "user_id": str(user_id)},
            {"$push": {"messages": safe_message}},
        )
        if result.modified_count == 0:
            logger.warning(
                f"[Mongo] Failed to append message: conversation not found "
                f"{conversation_id} for user {user_id}"
            )
        return result.modified_count

@lru_cache(maxsize=1)
def _repo_singleton() -> ConversationMongoRepository:
    return ConversationMongoRepository()

def get_conversation_mongo_repository() -> ConversationMongoRepository:
    return _repo_singleton()