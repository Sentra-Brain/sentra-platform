from datetime import datetime, timezone
from uuid import UUID
from pymongo import MongoClient
from sentra_core.infra.nosql.mongo_settings import settings
from sentra_core.core.logging import get_logger

logger = get_logger("sentra_brain_api.mongo_repository")

class MongoConversationRepository:
    """
    Repository for managing conversations in MongoDB.

    All conversation and user IDs are handled as Python UUID objects in the application layer.
    When storing or querying in MongoDB, these UUIDs are always cast to strings (str(UUID)).
    This ensures compatibility, readability, and interoperability with other tools and services
    that may access the database.

    When reading documents from MongoDB, the '_id' and 'user_id' fields will be strings.
    If your domain or API models require UUIDs, you should convert these fields back to UUID
    objects at the service or entity layer.

    This approach avoids BSON binary UUID storage and guarantees that all IDs are human-readable
    and consistent across the stack.
    """
    def __init__(self):
        self.client = MongoClient(
            settings.mongo_url,
            uuidRepresentation="standard"  # Use standard UUID representation for compatibility
        )
        self.db = self.client[settings.mongo_database]
        logger.info(f"[Mongo] Connected to database {settings.mongo_database} at {settings.mongo_host}:{settings.mongo_port}")

    def get_conversations_collection(self):
        return self.db["conversations"]

    def get_conversation_by_id(self, conversation_id: UUID, user_id: UUID) -> dict:
        collection = self.get_conversations_collection()
        doc = collection.find_one({
            "_id": str(conversation_id),
            "user_id": str(user_id)
        })
        if not doc:
            logger.warning(f"[Mongo] Conversation not found with ID {conversation_id} for user {user_id}")
            raise ValueError(f"Conversation not found: {conversation_id} for user: {user_id}")
        return doc
    
    def create_conversation(self, conversation_id: UUID, user_id: UUID, messages: list[dict], **fields) -> dict:
        collection = self.get_conversations_collection()
        doc = {
            "_id": str(conversation_id),
            "user_id": str(user_id),
            "created_at": datetime.now(timezone.utc),
            "messages": messages,
            **{k: v for k, v in fields.items() if v is not None and k != "initial_prompt"}
        }
        collection.insert_one(doc)
        logger.info(f"[Mongo] Created conversation with {len(messages)} messages")
        return doc
    
    def update_conversation(self, conversation_id: UUID, updates: dict) -> int:
        collection = self.get_conversations_collection()
        result = collection.update_one(
            {"_id": str(conversation_id)},
            {"$set": updates}
        )
        if result.modified_count == 0:
            logger.warning(f"[Mongo] No conversation found to update with ID {conversation_id}")
        return result.modified_count
    

    def _stringify_uuids(self, obj):
        from uuid import UUID
        if isinstance(obj, UUID):
            return str(obj)
        if isinstance(obj, dict):
            return {k: self._stringify_uuids(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [self._stringify_uuids(v) for v in obj]
        return obj

    def append_message(self, conversation_id: UUID, user_id: UUID | None, message: dict) -> int:
        collection = self.get_conversations_collection()
        safe_message = self._stringify_uuids(message)  # <-- NORMALIZE UUIDs to strings
        result = collection.update_one(
            {"_id": str(conversation_id), "user_id": str(user_id)},
            {"$push": {"messages": safe_message}}
        )
        if result.modified_count == 0:
            logger.warning(f"[Mongo] Failed to append message. Conversation not found: {conversation_id} for user: {user_id}")
        return result.modified_count

mongo_service_instance = MongoConversationRepository()

def get_conversation_mongo_repository() -> MongoConversationRepository:
    return mongo_service_instance