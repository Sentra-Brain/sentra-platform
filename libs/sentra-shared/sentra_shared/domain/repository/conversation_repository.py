# sentra_brain_api/features/conversation/repository.py

from sqlalchemy.orm import Session
from uuid import uuid4
from sentra_shared.domain.repository.base_repository import BaseRepository
from sentra_shared.domain.entities.conversation_entity import ConversationEntity


class ConversationRepository(BaseRepository[ConversationEntity]):
    def __init__(self, db: Session):
        super().__init__(ConversationEntity, db)

    def create_with_user_id(self, user_id: str) -> str:
        conversation_id = str(uuid4())
        conversation = ConversationEntity(id=conversation_id, user_id=user_id)
        self.db.add(conversation)
        self.db.commit()
        return conversation_id
    
    def get_by_user_id(self, user_id: str):
        return self.db.query(ConversationEntity).filter(ConversationEntity.user_id == user_id).all()
    
    def update_title(self, conversation_id: str, title: str):
        conversation = self.get(conversation_id)
        if conversation:
            conversation.title = title
            self.db.commit()
        
