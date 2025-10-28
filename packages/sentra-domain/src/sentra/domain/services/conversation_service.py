from typing import Optional
from uuid import UUID
from sentra.domain.entities.conversation_entity import ConversationEntity
from sentra.domain.entities.user_entity import UserEntity
from sentra.domain.repository.conversation_repository import (
    IConversationSQLRepository,
    IConversationNoSQLRepository,
)


class ConversationService:
    """Domain service coordinating SQL (metadata) and NoSQL (runtime data)."""

    def __init__(
        self,
        sql_repo: IConversationSQLRepository,
        nosql_repo: IConversationNoSQLRepository,
    ):
        self.sql_repo = sql_repo
        self.nosql_repo = nosql_repo

    # -------------------------------------------------------------------------
    # CREATE
    # -------------------------------------------------------------------------
    def create_conversation(
        self,
        user: UserEntity,
        conversation: ConversationEntity,
        initial_user_prompt: str | None = None,
    ) -> ConversationEntity:
        """Create the conversation in SQL, mirror it in NoSQL."""
        conversation = self.sql_repo.create(conversation)

        # mirror in Mongo / NoSQL
        self.nosql_repo.create_conversation(
            conversation_id=conversation.id,
            user_id=user.id,
            title=conversation.title,
            created_at=conversation.created_at.isoformat(),
        )

        return conversation

    # -------------------------------------------------------------------------
    # READ
    # -------------------------------------------------------------------------
    def get_user_conversations(self, user_id: UUID) -> list[ConversationEntity]:
        """Return SQL-level conversation list."""
        return self.sql_repo.get_conversations_by_user_id(user_id)

    def get_conversation(self, conversation_id: UUID, user_id: UUID) -> dict:
        """Return runtime conversation (messages, metadata) from NoSQL."""
        return self.nosql_repo.get_conversation_by_id(conversation_id, user_id)

    # -------------------------------------------------------------------------
    # UPDATE
    # -------------------------------------------------------------------------
    def update_conversation(
        self,
        conversation_id: UUID,
        user_id: UUID,
        title: Optional[str],
        description: Optional[str],
    ) -> Optional[ConversationEntity]:
        conversation = self.sql_repo.get(conversation_id)
        if not conversation:
            return None

        if title:
            conversation.title = title
        if description:
            conversation.description = description

        self.sql_repo.update(conversation)
        self.nosql_repo.update_conversation(
            conversation_id,
            {"title": title, "description": description},
        )

        return conversation

    def update_title(self, conversation_id: UUID, user_id: UUID, title: str):
        """Keep SQL and NoSQL titles consistent."""
        self.sql_repo.update_title(conversation_id, title)
        self.nosql_repo.update_conversation(conversation_id, {"title": title})

    # -------------------------------------------------------------------------
    # DELETE
    # -------------------------------------------------------------------------
    def delete_conversation(self, conversation_id: UUID, user_id: UUID) -> bool:
        """Delete from both SQL and NoSQL."""
        deleted = False

        conversation = self.sql_repo.get(conversation_id)
        if conversation and conversation.created_by_id == user_id:
            self.sql_repo.delete(conversation_id)
            deleted = True

        self.nosql_repo.delete_conversation(conversation_id, user_id)
        return deleted
