from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sentra_brain_api.crosscutting.authorization import get_authenticated_user
from sentra_core.domain.entities.user_entity import UserEntity
from sentra_brain_api.features.conversation.api_service import ConversationApiService
from sentra_core.infra.nosql.mongo_conversation_repository import MongoConversationRepository, get_conversation_mongo_repository
from sentra_core.infra.sql.postgres_service import get_db

from sentra_brain_api.features.conversation.schemas import (
    ConversationListItemResponse,
    ConversationResponse,
    CreateConversationRequest,
    CreateConversationResponse,
    DeleteConversationResponse,
    UpdateConversationRequest,
    UpdateConversationResponse,
)


class ConversationController:
    def __init__(self):
        self.router = APIRouter()
        self._add_routes()

    def _get_service(
        self,
        db: Session = Depends(get_db),
        mongo_repo: MongoConversationRepository = Depends(get_conversation_mongo_repository)
    ) -> ConversationApiService:
        return ConversationApiService(db=db, mongo_repo=mongo_repo)

    def _add_routes(self):
        @self.router.post(
            "/",
            response_model=CreateConversationResponse,
            description="Creates a new conversation for the current user"
        )
        async def create_conversation(
            body: CreateConversationRequest,
            current_user: UserEntity = Depends(get_authenticated_user),
            service: ConversationApiService = Depends(self._get_service)
        ):
            return await service.create_conversation(current_user, body)
        
        @self.router.post(
            "/{conversation_id}/generate-title",
            response_model=UpdateConversationResponse,
            description="Generate a better conversation title using LLM"
        )
        async def generate_llm_title_for_conversation(
            conversation_id: UUID,
            current_user: UserEntity = Depends(get_authenticated_user),
            service: ConversationApiService = Depends(self._get_service),
        ):
            return await service.generate_llm_title_for_conversation(current_user, conversation_id)

        @self.router.get(
            "/",
            response_model=list[ConversationListItemResponse],
            description="Retrieves all conversations for the current user"
        )
        def get_conversations(
            current_user: UserEntity = Depends(get_authenticated_user),
            service: ConversationApiService = Depends(self._get_service)
        ):
            return service.list_user_conversations(current_user)

        @self.router.get(
            "/{conversation_id}",
            response_model=ConversationResponse,
            description="Retrieve a specific conversation by its ID"
        )
        def get_conversation_by_id(
            conversation_id: UUID,
            current_user: UserEntity = Depends(get_authenticated_user),
            service: ConversationApiService = Depends(self._get_service)
        ):
            return service.get_conversation(current_user, conversation_id)

        @self.router.put(
            "/{conversation_id}",
            response_model=UpdateConversationResponse,
            description="Update title and description of a conversation"
        )
        def update_conversation(
            conversation_id: UUID,
            request: UpdateConversationRequest,
            current_user: UserEntity = Depends(get_authenticated_user),
            service: ConversationApiService = Depends(self._get_service)
        ):
            return service.update_conversation(current_user, conversation_id, request)

        @self.router.delete(
            "/{conversation_id}",
            response_model=DeleteConversationResponse,
            description="Delete a conversation"
        )
        def delete_conversation(
            conversation_id: UUID,
            current_user: UserEntity = Depends(get_authenticated_user),
            service: ConversationApiService = Depends(self._get_service)
        ):
            return service.delete_conversation(current_user, conversation_id)
