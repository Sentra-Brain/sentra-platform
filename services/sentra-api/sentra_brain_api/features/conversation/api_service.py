# sentra_brain_api/features/conversation/api_service.py

import uuid
from sqlalchemy.orm import Session
from sentra_core.core.logging import get_logger
from sentra_core.domain.entities.conversation_entity import ConversationEntity
from sentra_core.domain.entities.user_entity import UserEntity
from sentra_core.domain.repository.conversation_repository import ConversationRepository
from sentra_core.domain.services.conversation_service import ConversationService
from sentra_core.infra.nosql.mongo_conversation_repository import MongoConversationRepository

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
    entity_to_creation_response,
    entity_to_list_item_response,
    mongo_doc_to_response
)
from sentra_brain_api.core.exceptions import SentraHTTPException

logger = get_logger("conversation_api_service")

class ConversationApiService:
    def __init__(self, db: Session, mongo_repo: MongoConversationRepository):
        self.service = ConversationService(
            sql_repo=ConversationRepository(db),
            mongo_repo=mongo_repo
        )
        self.title_service = TitleGenerationService()

    async def create_conversation(self, user: UserEntity, request: CreateConversationRequest) -> CreateConversationResponse:
        # Determine the title before creating the conversation
        title = request.title
        if not title and request.content:
            try:
                title = self.title_service.generate_initial_title(request.content)
            except Exception as e:
                logger.warning(f"Failed to generate initial title: {e}")
                title = None

        # Create and persist conversation with precomputed title
        conversation = ConversationEntity(
            created_by_id=user.id,
            title=title,
            description=request.description,
            initial_prompt=request.initial_prompt,
        )

        conversation = self.service.create_conversation(
            user=user,
            conversation=conversation,
        )

        return entity_to_creation_response(conversation)

    async def generate_llm_title(self, user: UserEntity, conversation_id: uuid.UUID) -> str:
        # 1. Get conversation and messages
        conversation = self.service.get_conversation(conversation_id, user.id)
        if not conversation:
            raise SentraHTTPException(
                status_code=404,
                detail="Conversation not found"
            )

        # 2. Generate LLM title
        llm_title = await self.title_service.generate_llm_title(conversation.initial_prompt)
        if not llm_title:
            raise SentraHTTPException(
                status_code=500,
                detail="Failed to generate title"
            )

        # 3. Update title
        self.service.update_title(conversation_id, str(user.id), llm_title)

        return llm_title

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
