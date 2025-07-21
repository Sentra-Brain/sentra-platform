# sentra_brain_api/features/conversation/controller.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sentra_brain_api.domain.user_entity import UserEntity
from sentra_brain_api.features.user.models import UserModel
from sentra_brain_api.infra.postgres_service import get_db
from sentra_brain_api.crosscutting.authorization import get_authenticated_user
from sentra_brain_api.crosscutting import logging
from sentra_brain_api.features.conversation.models import (
    CreateConversationRequest,
    CreateConversationResponse
)
from sentra_brain_api.features.conversation.repository import ConversationRepository
from sentra_brain_api.features.conversation.conversation_service import ConversationService

logger = logging.get_logger("sentra_brain_api")


class ConversationController:
    def __init__(self):
        self.router = APIRouter()
        self._add_routes()

    def _add_routes(self):
        @self.router.post(
            "/api/conversations",
            response_model=CreateConversationResponse,
            description="Creates a new conversation for the current user"
        )
        def create_conversation(
            body: CreateConversationRequest,
            current_user: UserEntity = Depends(get_authenticated_user),
            db: Session = Depends(get_db),
        ):
            logger.info(f"Creating conversation for user {current_user.id}")
            repo = ConversationRepository(db)
            service = ConversationService(repo)
            conversation_id = service.create_conversation(user_id=current_user.id)
            return CreateConversationResponse(conversation_id=conversation_id)
