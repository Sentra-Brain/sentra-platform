from datetime import datetime, timezone
from uuid import UUID
from pymongo import MongoClient
from sentra_core.infra.nosql.mongo_settings import settings
from sentra_core.core.logging import get_logger

logger = get_logger("sentra_brain_api.mongo_repository")

class MongoConversationRepository:
    def __init__(self):
        self.client = MongoClient(
            settings.mongo_url,
            uuidRepresentation="standard"  # important for UUID handling
        )
        self.db = self.client[settings.mongo_database]
        logger.info(f"[Mongo] Connected to database {settings.mongo_database} at {settings.mongo_host}:{settings.mongo_port}")

    def get_conversations_collection(self):
        return self.db["conversations"]

    def get_conversation_by_id(self, conversation_id: UUID, user_id: UUID) -> dict | None:
        collection = self.get_conversations_collection()
        doc = collection.find_one({
            "_id": str(conversation_id),
            "user_id": str(user_id)
        })
        if not doc:
            logger.warning(f"[Mongo] Conversation not found with ID {conversation_id} for user {user_id}")
        return doc
    
    def create_conversation(self, conversation_id: UUID, user_id: UUID, messages: list[dict], **fields) -> dict:
        collection = self.get_conversations_collection()
        doc = {
            "_id": str(conversation_id),
            "user_id": str(user_id),
            "initial_prompt": fields.get("initial_prompt", ""),
            "created_at": datetime.now(timezone.utc),
            "messages": messages,
            **{k: v for k, v in fields.items() if v is not None} 
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
    
    def append_message(self, conversation_id: UUID, user_id: UUID, message: dict) -> int:
        collection = self.get_conversations_collection()
        result = collection.update_one(
            {
                "_id": str(conversation_id),
                "user_id": str(user_id)
            },
            {
                "$push": {"messages": message}
            }
        )
        if result.modified_count == 0:
            logger.warning(f"[Mongo] Failed to append message. Conversation not found: {conversation_id} for user: {user_id}")
        return result.modified_count


mongo_service_instance = MongoConversationRepository()

def get_conversation_mongo_repository() -> MongoConversationRepository:
    return mongo_service_instance