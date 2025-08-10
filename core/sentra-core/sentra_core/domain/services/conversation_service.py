# sentra_core/domain/services/conversation_service.py

from datetime import datetime, timezone, timedelta
from typing import Optional
from uuid import UUID

from sentra_core.domain.entities.conversation_entity import ConversationEntity
from sentra_core.domain.entities.user_entity import UserEntity
from sentra_core.domain.repository.conversation_repository import ConversationRepository
from sentra_core.core.constants import SYSTEM_PROMPT
from sentra_core.infra.nosql.mongo_conversation_repository import MongoConversationRepository


class ConversationService:
    def __init__(self, sql_repo: ConversationRepository, mongo_repo: MongoConversationRepository):
        self.sql_repo = sql_repo
        self.mongo_repo = mongo_repo

    def create_conversation(self, user: UserEntity, conversation: ConversationEntity, initial_user_prompt: str | None = None) -> ConversationEntity:
        conversation = self.sql_repo.create(conversation)

        messages = [{
            "role": "system",
            "content": SYSTEM_PROMPT,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "is_system_prompt": True
        }]
        if initial_user_prompt:
            messages.append({
                "role": "user",
                "content": initial_user_prompt,
                "timestamp": (datetime.now(timezone.utc) + timedelta(milliseconds=1)).isoformat()
            })

        self.mongo_repo.create_conversation(
            conversation_id=conversation.id,
            user_id=user.id,
            messages=messages,
            title=conversation.title,
            created_at=conversation.created_at.isoformat()
        )

        return conversation

    def get_user_conversations(self, user_id: UUID) -> list[ConversationEntity]:
        return self.sql_repo.get_conversations_by_user_id(user_id)

    def get_conversation(self, conversation_id: UUID, user_id: UUID) -> dict:
        return self.mongo_repo.get_conversation_by_id(conversation_id, user_id)

    def update_conversation(self, conversation_id: UUID, user_id: UUID, title: Optional[str], description: Optional[str]) -> Optional[ConversationEntity]:
        conversation = self.sql_repo.get(conversation_id)
        if not conversation:
            return None

        if title:
            conversation.title = title
        if description:
            conversation.description = description

        self.sql_repo.update(conversation)

        self.mongo_repo.get_conversations_collection().update_one(
            {"_id": conversation_id, "user_id": user_id},
            {"$set": {
                "title": title,
                "description": description
            }}
        )

        return conversation

    def delete_conversation(self, conversation_id: UUID, user_id: UUID) -> bool:
        deleted = False

        conversation = self.sql_repo.get(conversation_id)
        if conversation and conversation.created_by_id == user_id:
            self.sql_repo.delete(conversation_id)
            deleted = True

        result = self.mongo_repo.get_conversations_collection().delete_one({
            "_id": conversation_id,
            "user_id": user_id
        })

        return deleted or result.deleted_count > 0

    def update_title(self, conversation_id: UUID, user_id: UUID, title: str):
        self.sql_repo.update_title(conversation_id, title)
        self.mongo_repo.update_conversation(conversation_id, {"title": title})
