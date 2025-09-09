# packages/sentra-infra/src/sentra/infra/nosql/mongo_session_repository.py
from datetime import datetime, timezone
from functools import lru_cache
from uuid import UUID
from pymongo import MongoClient
from sentra.infra.nosql.mongo_settings import settings
from sentra.shared.logging import get_logger

logger = get_logger("sentra.infra.nosql.mongo_session_repository")


class MongoSessionRepository:
    """Repository for managing chat sessions in MongoDB."""

    def __init__(self):
        self.client = MongoClient(
            settings.mongo_url,
            uuidRepresentation="standard",  # Use standard UUID representation for compatibility
        )
        self.db = self.client[settings.mongo_database]
        self.get_sessions_collection().create_index(
            [("user_id", 1), ("_id", 1)], name="by_user_and_id"
        )
        logger.info(
            f"[Mongo] Connected to database {settings.mongo_database} at {settings.mongo_host}:{settings.mongo_port}"
        )

    # Collections -----------------------------------------------------------------
    def get_sessions_collection(self):
        return self.db["sessions"]

    # CRUD ------------------------------------------------------------------------
    def get_session_by_id(self, session_id: UUID, user_id: UUID) -> dict:
        collection = self.get_sessions_collection()
        doc = collection.find_one({"_id": str(session_id), "user_id": str(user_id)})
        if not doc:
            logger.warning(
                f"[Mongo] Session not found with ID {session_id} for user {user_id}"
            )
            raise ValueError(f"Session not found: {session_id} for user: {user_id}")
        return doc

    def create_session(self, session_id: UUID, user_id: UUID, **fields) -> dict:
        collection = self.get_sessions_collection()
        doc = {
            "_id": str(session_id),
            "user_id": str(user_id),
            "created_at": datetime.now(timezone.utc),
            "events": [],
            **{k: v for k, v in fields.items() if v is not None and k != "initial_prompt"},
        }
        collection.insert_one(doc)
        logger.info(
            f"[Mongo] Created session placeholder for ID {session_id} and user {user_id}"
        )
        return doc

    def update_session(self, session_id: UUID, updates: dict) -> int:
        collection = self.get_sessions_collection()
        result = collection.update_one({"_id": str(session_id)}, {"$set": updates})
        if result.modified_count == 0:
            logger.warning(
                f"[Mongo] No session found to update with ID {session_id}"
            )
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

    def append_event(self, session_id: UUID, user_id: UUID | None, event: dict) -> int:
        collection = self.get_sessions_collection()
        safe_event = self._stringify_uuids(event)  # <-- NORMALIZE UUIDs to strings
        result = collection.update_one(
            {"_id": str(session_id), "user_id": str(user_id)},
            {"$push": {"events": safe_event}},
        )
        if result.modified_count == 0:
            logger.warning(
                f"[Mongo] Failed to append event. Session not found: {session_id} for user: {user_id}"
            )
        return result.modified_count

@lru_cache(maxsize=1)
def _repo_singleton() -> MongoSessionRepository:
    return MongoSessionRepository()

def get_session_mongo_repository() -> MongoSessionRepository:
    return _repo_singleton()