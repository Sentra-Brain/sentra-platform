# sentra_brain_api/features/conversation/conversation_service.py

from sentra_brain_api.features.conversation.repository import ConversationRepository


class ConversationService:
    def __init__(self, repository: ConversationRepository):
        self.repository = repository

    def create_conversation(self, user_id: str) -> str:
        return self.repository.create(user_id)
