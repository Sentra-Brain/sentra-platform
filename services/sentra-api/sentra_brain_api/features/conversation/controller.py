# sentra_brain_api/features/conversation/controller.py

from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sentra_brain_api.core.exceptions import SentraHTTPException
from sentra_brain_api.domain.conversation_entity import ConversationEntity
from sentra_brain_api.domain.user_entity import UserEntity
from sentra_brain_api.infra.mongo_conversation_repository import MongoConversationRepository, get_conversation_mongo_repository
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
            "/",
            response_model=CreateConversationResponse,
            description="Creates a new conversation for the current user"
        )
        def create_conversation(
            body: CreateConversationRequest,
            current_user: UserEntity = Depends(get_authenticated_user),
            db: Session = Depends(get_db),
            mongo: MongoConversationRepository = Depends(get_conversation_mongo_repository)
        ):
                logger.info(f"Creating conversation for user {current_user.id}")

                try:
                    # 1. PostgreSQL – save conversation metadata
                    conversation = ConversationEntity(
                        user_id=current_user.id,
                        title=body.title,
                        description=body.description,
                        initial_prompt=body.initial_prompt
                    )

                    repo = ConversationRepository(db)
                    service = ConversationService(repo)
                    conversation = service.create_conversation(conversation)

                except Exception as e:
                    raise SentraHTTPException(
                        status_code=500,
                        code="PG_SAVE_FAILED",
                        message="Failed to create conversation in the database.",
                        details=str(e),
                        path="/conversations/",
                        suggestion="Check database connection and conversation constraints."
                    )

                try:
                    # 2. MongoDB – save initial messages
                    messages = []

                    if body.initial_prompt:
                        messages.append({
                            "role": "system",
                            "content": body.initial_prompt,
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        })

                    delta = timedelta(milliseconds=1)

                    messages.append({
                        "role": "user",
                        "content": body.content,
                        "timestamp": (datetime.now(timezone.utc) + delta).isoformat()
                    })

                    mongo.create_conversation_with_messages(
                        conversation_id=str(conversation.id),
                        user_id=str(current_user.id),
                        messages=messages
                    )


                except Exception as e:
                    raise SentraHTTPException(
                        status_code=500,
                        code="MONGO_INSERT_FAILED",
                        message="Failed to store conversation messages.",
                        details=str(e),
                        path="/conversations/",
                        suggestion="Check MongoDB availability and message structure."
                    )

                return CreateConversationResponse(conversation_id=conversation.id)
        
        @self.router.get(
            "/",
            response_model=list[CreateConversationResponse],
            description="Retrieves all conversations for the current user"
        )
        def get_conversations(
            current_user: UserEntity = Depends(get_authenticated_user),
            db: Session = Depends(get_db),
        ):
            logger.info(f"Retrieving conversations for user {current_user.id}")
            repo = ConversationRepository(db)
            service = ConversationService(repo)
            conversations = service.get_user_conversations(user_id=current_user.id)
            return [CreateConversationResponse(conversation_id=conv.id) for conv in conversations]
