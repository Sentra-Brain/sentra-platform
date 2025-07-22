from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sentra_brain_api.crosscutting.authorization import get_authenticated_user
from sentra_brain_api.crosscutting import logging
from sentra_brain_api.domain.user_entity import UserEntity
from sentra_brain_api.infra.mongo_conversation_repository import MongoConversationRepository, get_conversation_mongo_repository
from sentra_brain_api.infra.postgres_service import get_db
from sentra_brain_api.features.conversation.repository import ConversationRepository
from sentra_brain_api.features.conversation.models import (
    ConversationListItemModel,
    ConversationModel,
    CreateConversationRequest,
    CreateConversationResponse,
    DeleteConversationResponse,
    UpdateConversationRequest,
    UpdateConversationResponse,
)
from sentra_brain_api.features.conversation.conversation_management_service import ConversationManagementService

logger = logging.get_logger("sentra_brain_api")


class ConversationManagementController:
    def __init__(self):
        self.router = APIRouter()
        self._add_routes()   
    

    def _get_service(
            self,
            db: Session = None,
            mongo_repo: MongoConversationRepository = None
    ) -> ConversationManagementService:
            return ConversationManagementService(
                sql_repo=ConversationRepository(db) if db else None,
                mongo_repo=mongo_repo
            )

    def _add_routes(self):
        @self.router.post(
            "/",
            response_model=CreateConversationResponse,
            description="Creates a new conversation for the current user"
        )
        def create_conversation(
            body: CreateConversationRequest,
            current_user: UserEntity = Depends(get_authenticated_user),
            db: Session = Depends(get_db),
            nosql_repo: MongoConversationRepository = Depends(get_conversation_mongo_repository)
        ):
            service = self._get_service(db=db, mongo_repo=nosql_repo)
            conversation_id = service.create_conversation(current_user, body)
            return CreateConversationResponse(conversation_id=conversation_id)

        @self.router.get(
            "/",
            response_model=list[ConversationListItemModel],
            description="Retrieves all conversations for the current user"
        )
        def get_conversations(
            current_user: UserEntity = Depends(get_authenticated_user),
            db: Session = Depends(get_db),
        ):
            service = self._get_service(db=db)
            conversations = service.get_user_conversations(current_user)
            return [
                ConversationListItemModel(
                    conversation_id=str(conv.id),
                    title=conv.title or "Untitled",
                    created_at=conv.created_at
                )
                for conv in conversations
            ]

        @self.router.get(
            "/{conversation_id}",
            response_model=ConversationModel,
            description="Retrieve a specific conversation by its ID"
        )
        def get_conversation_by_id(
            conversation_id: str,
            current_user: UserEntity = Depends(get_authenticated_user),
            nosql_repo: MongoConversationRepository = Depends(get_conversation_mongo_repository),
        ):
            service = self._get_service(mongo_repo=nosql_repo)
            conversation_data = service.get_conversation(current_user, conversation_id)
            return ConversationModel(**conversation_data)

        @self.router.put(
            "/{conversation_id}",
            response_model=UpdateConversationResponse,
            description="Update title and description of a conversation"
        )
        def update_conversation(
            conversation_id: str,
            request: UpdateConversationRequest,
            current_user: UserEntity = Depends(get_authenticated_user),
            db: Session = Depends(get_db),
            nosql_repo: MongoConversationRepository = Depends(get_conversation_mongo_repository)
        ):
            service = self._get_service(db=db, mongo_repo=nosql_repo)
            updated = service.update_conversation(current_user, conversation_id, request)
            return UpdateConversationResponse(
                conversation_id=str(updated.id),
                title=updated.title,
                description=updated.description
            )

        @self.router.delete(
            "/{conversation_id}",
            response_model=DeleteConversationResponse,
            description="Delete a conversation"
        )
        def delete_conversation(
            conversation_id: str,
            current_user: UserEntity = Depends(get_authenticated_user),
            db: Session = Depends(get_db),
            nosql_repo: MongoConversationRepository = Depends(get_conversation_mongo_repository)
        ):
            service = self._get_service(db=db, mongo_repo=nosql_repo)
            service.delete_conversation(current_user, conversation_id)
            return DeleteConversationResponse(
                success=True,
                message="Conversation deleted successfully"
            )
