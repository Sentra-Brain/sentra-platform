# sentra_brain_api/features/conversation/conversation_service.py
from sentra_shared.domain.entities.conversation_entity import ConversationEntity
from sentra_shared.domain.repository.conversation_repository import ConversationRepository


class ConversationService:
    def __init__(self, repository: ConversationRepository):
        self.repository = repository

    def get_conversation(self, conversation_id: str) -> ConversationEntity:
        conversation = self.repository.get(conversation_id)
        if not conversation:
            raise ValueError("Conversation not found")
        return conversation

    def create_conversation(self, conversation: ConversationEntity) -> ConversationEntity:
        return self.repository.create(conversation)

    def get_user_conversations(self, user_id: str):
        return self.repository.get_by_user_id(user_id)
    
    def update_conversation(self, conversation_id: str, title: str = None, description: str = None) -> ConversationEntity:
        conversation = self.repository.get(conversation_id)
        if not conversation:
            raise ValueError("Conversation not found")
        
        if title is not None:
            conversation.title = title
        if description is not None:
            conversation.description = description
        
        self.repository.update(conversation)
        return conversation
    
    def delete_conversation(self, conversation_id: str):
        conversation = self.repository.get(conversation_id)
        if not conversation:
            raise ValueError("Conversation not found")
        
        self.repository.delete(conversation_id)
        return {"message": "Conversation deleted successfully"}