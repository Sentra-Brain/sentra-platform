"""Domain service for managing chat sessions."""

from typing import Optional
from uuid import UUID

from sentra.domain.entities.conversation_entity import ConversationEntity
from sentra.domain.entities.user_entity import UserEntity
from sentra.domain.repository.conversation_repository import IConversationRepository


class ConversationService:
    def __init__(self, sql_repo: IConversationRepository):
        self.sql_repo = sql_repo

    def create_conversation(self, user: UserEntity, conversation: ConversationEntity, initial_user_prompt: str | None = None) -> ConversationEntity:
        conversation = self.sql_repo.create(conversation)
        return conversation

    def get_user_conversations(self, user_id: UUID) -> list[ConversationEntity]:
        return self.sql_repo.get_conversations_by_user_id(user_id)

    def get_conversation(self, conversation_id: UUID) -> ConversationEntity | None:
        return self.sql_repo.get(conversation_id)

    def update_conversation(
        self, conversation_id: UUID, title: Optional[str], description: Optional[str]
    ) -> Optional[ConversationEntity]:
        conversation = self.sql_repo.get(conversation_id)
        if not conversation:
            return None

        if title:
            conversation.title = title
        if description:
            conversation.description = description

        self.sql_repo.update(conversation)
        return conversation

    def delete_conversation(self, conversation_id: UUID, user_id: UUID) -> bool:
        conversation = self.sql_repo.get(conversation_id)
        if conversation and conversation.created_by_id == user_id:
            self.sql_repo.delete(conversation_id)
            return True
        return False

    def update_title(self, conversation_id: UUID, title: str):
        self.sql_repo.update_title(conversation_id, title)

    # State management is now handled by ADK or other persistent layer if needed.
