# sentra_brain_api/features/conversation/conversation_service.py
from sentra_brain_api.domain.conversation_entity import ConversationEntity
from sentra_brain_api.features.conversation.repository import ConversationRepository


class ConversationService:
    def __init__(self, repository: ConversationRepository):
        self.repository = repository

    def create_conversation(self, conversation: ConversationEntity) -> ConversationEntity:
        return self.repository.create(conversation)

    def get_user_conversations(self, user_id: str):
        return self.repository.get_by_user_id(user_id)