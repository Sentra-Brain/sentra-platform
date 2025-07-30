# sentra_brain_api/features/conversation/api_service.py

from sqlalchemy.orm import Session
from sentra_shared.domain.services.conversation_service import ConversationService
from sentra_shared.domain.repository.conversation_repository import ConversationRepository
from sentra_shared.infra.nosql.mongo_conversation_repository import MongoConversationRepository
from sentra_shared.domain.entities.conversation_entity import ConversationEntity
from sentra_shared.domain.entities.user_entity import UserEntity

from sentra_brain_api.features.conversation.schemas import (
    CreateConversationRequest,
    CreateConversationResponse,
    ConversationListItemResponse,
    ConversationResponse,
    UpdateConversationRequest,
    UpdateConversationResponse,
    DeleteConversationResponse
)
from sentra_brain_api.features.conversation.title.title_generation_service import TitleGenerationService
from sentra_brain_api.features.conversation.mappers import (
    entity_to_list_item_response,
    mongo_doc_to_response
)
from sentra_brain_api.core.exceptions import SentraHTTPException


class ConversationApiService:
    def __init__(self, db: Session, mongo_repo: MongoConversationRepository):
        self.service = ConversationService(
            sql_repo=ConversationRepository(db),
            mongo_repo=mongo_repo
        )
        self.title_service = TitleGenerationService()

    async def create_conversation(self, user: UserEntity, request: CreateConversationRequest) -> CreateConversationResponse:
        conversation = ConversationEntity(
            created_by_id=user.id,
            title=request.title,
            description=request.description,
            initial_prompt=request.initial_prompt
        )

        conversation_id = self.service.create_conversation(user, request.content, conversation)

        if not request.title and request.content:
            try:
                title = await self.title_service.generate_title(request.content)
                self.service.update_title(conversation_id, str(user.id), title)
            except Exception:
                pass

        return CreateConversationResponse(id=conversation_id)

    def list_user_conversations(self, user: UserEntity) -> list[ConversationListItemResponse]:
        conversations = self.service.get_user_conversations(user.id)
        return [
            entity_to_list_item_response(conv)
            for conv in conversations
        ]

    def get_conversation(self, user: UserEntity, conversation_id: str) -> ConversationResponse:
        doc = self.service.get_conversation(conversation_id, str(user.id))
        if not doc:
            raise SentraHTTPException.not_found("Conversation not found")
        return mongo_doc_to_response(doc)

    def update_conversation(self, user: UserEntity, conversation_id: str, req: UpdateConversationRequest) -> UpdateConversationResponse:
        updated = self.service.update_conversation(
            conversation_id=conversation_id,
            user_id=str(user.id),
            title=req.title,
            description=req.description
        )

        if not updated:
            raise SentraHTTPException.not_found("Conversation not found")

        return UpdateConversationResponse(
            conversation_id=conversation_id,
            title=updated.title,
            description=updated.description
        )

    def delete_conversation(self, user: UserEntity, conversation_id: str) -> DeleteConversationResponse:
        deleted = self.service.delete_conversation(conversation_id, str(user.id))

        if not deleted:
            raise SentraHTTPException.not_found("Conversation not found")

        return DeleteConversationResponse(
            success=True,
            message="Conversation deleted successfully"
        )
