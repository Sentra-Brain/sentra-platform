# sentra_brain_api/infra/mongo_service.py

from datetime import datetime, timezone
from pymongo import MongoClient
from sentra_brain_api.core.config import settings
from sentra_brain_api.crosscutting.logging import get_logger

logger = get_logger("sentra_brain_api.mongo_service")

class MongoConversationRepository:
    def __init__(self):
        self.client = MongoClient(settings.mongo_url)
        self.db = self.client[settings.mongo_database]
        logger.info(f"[Mongo] Connected to database {settings.mongo_database} at {settings.mongo_host}:{settings.mongo_port}")

    def get_conversations_collection(self):
        return self.db["conversations"]

    def add_message_to_conversation(self, conversation_id: str, message: dict):
        collection = self.get_conversations_collection()
        result = collection.update_one(
            {"_id": conversation_id},
            {"$push": {"messages": message}},
            upsert=True  # In case the conversation doc doesn't exist yet
        )
        return result.modified_count

    def create_conversation(self, conversation_id: str, user_id: int, first_message: dict):
        collection = self.get_conversations_collection()
        doc = {
            "_id": conversation_id,
            "user_id": user_id,
            "messages": [first_message],
        }
        collection.insert_one(doc)
        logger.info(f"[Mongo] Created conversation document {conversation_id} for user {user_id}")
        return doc
    
    def create_conversation_with_messages(self, conversation_id: str, user_id: str, messages: list[dict]):
        collection = self.get_conversations_collection()
        doc = {
            "_id": conversation_id,
            "user_id": user_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "messages": messages
        }
        collection.insert_one(doc)
        logger.info(f"[Mongo] Created conversation with {len(messages)} messages")
        return doc



mongo_service_instance = MongoConversationRepository()

def get_conversation_mongo_repository() -> MongoConversationRepository:
    return mongo_service_instance