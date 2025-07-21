# sentra_brain_api/features/conversation/repository.py

from sqlalchemy.orm import Session
from uuid import uuid4
from sentra_brain_api.core.base_repository import BaseRepository
from sentra_brain_api.domain.conversation_entity import ConversationEntity


class ConversationRepository(BaseRepository[ConversationEntity]):
    def __init__(self, db: Session):
        super().__init__(ConversationEntity, db)

    def create_with_user_id(self, user_id: str) -> str:
        conversation_id = str(uuid4())
        conversation = ConversationEntity(id=conversation_id, user_id=user_id)
        self._db.add(conversation)
        self._db.commit()
        return conversation_id
