# packages/sentra-infra/src/sentra/infra/sql/repositories/session_repository_sql.py
from sqlalchemy.orm import Session
from sentra.domain.entities.conversation_entity import ConversationEntity
from sentra.domain.repository.conversation_repository import IConversationRepository
from sentra.infra.sql.repositories.base_repository import BaseRepository
from uuid import UUID, uuid4

class ConversationRepositorySql(BaseRepository[ConversationEntity], IConversationRepository):
    def __init__(self, db: Session):
        super().__init__(ConversationEntity, db)

    def create_with_user_id(self, user_id: UUID) -> UUID:
        conversation_id = uuid4()
        conversation = ConversationEntity(id=conversation_id, created_by_id=user_id)
        self.db.add(conversation)
        self.db.commit()
        return conversation_id

    def get_conversations_by_user_id(self, user_id: UUID) -> list[ConversationEntity]:
        return self.db.query(ConversationEntity).filter(ConversationEntity.created_by_id == user_id).all()

    def update_title(self, conversation_id: UUID, title: str) -> None:
        conversation = self.get(conversation_id)
        if conversation:
            conversation.title = title
            self.db.commit()
