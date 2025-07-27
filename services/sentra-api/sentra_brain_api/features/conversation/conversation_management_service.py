from datetime import datetime, timezone, timedelta
from typing import List

from sentra_brain_api.core.exceptions import SentraHTTPException
from sentra_shared.core.logging import get_logger
from sentra_shared.domain.entities.conversation_entity import ConversationEntity
from sentra_shared.domain.entities.user_entity import UserEntity
from sentra_shared.domain.repositories.conversation_repository import ConversationRepository
from sentra_brain_api.features.conversation.conversation_service import ConversationService
from sentra_brain_api.features.conversation.models import (
    CreateConversationRequest,
    UpdateConversationRequest,
)
from sentra_shared.infra.nosql.mongo_conversation_repository import MongoConversationRepository

logger = get_logger("sentra_brain_api")

class ConversationManagementService:
    def __init__(self, sql_repo: ConversationRepository, mongo_repo: MongoConversationRepository):
        self.sql_service = ConversationService(sql_repo)
        self.mongo_repo = mongo_repo

    def create_conversation(self, user: UserEntity, request: CreateConversationRequest) -> str:
        try:
            conversation = ConversationEntity(
                user_id=user.id,
                title=request.title,
                description=request.description,
                initial_prompt=request.initial_prompt
            )
            conversation = self.sql_service.create_conversation(conversation)
        except Exception as e:
            logger.error(f"Failed to create conversation in SQL: {str(e)}")
            raise SentraHTTPException(
                status_code=500,
                code="PG_SAVE_FAILED",
                message="Failed to create conversation in the database.",
                details=str(e),
                path="/conversations/",
                suggestion="Check database connection and conversation constraints."
            )

        try:
            messages = []

            if request.initial_prompt:
                messages.append({
                    "role": "system",
                    "content": request.initial_prompt,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })

            delta = timedelta(milliseconds=1)
            messages.append({
                "role": "user",
                "content": request.content,
                "timestamp": (datetime.now(timezone.utc) + delta).isoformat()
            })

            self.mongo_repo.create_conversation(
                conversation_id=str(conversation.id),
                user_id=str(user.id),
                messages=messages,
                title=request.title,
                description=request.description,
                initial_prompt=request.initial_prompt,
                created_at=datetime.now(timezone.utc).isoformat()
            )

        except Exception as e:
            logger.error(f"Failed to store conversation messages in MongoDB: {str(e)}")
            raise SentraHTTPException(
                status_code=500,
                code="MONGO_INSERT_FAILED",
                message="Failed to store conversation messages.",
                details=str(e),
                path="/conversations/",
                suggestion="Check MongoDB availability and message structure."
            )

        return str(conversation.id)

    def get_user_conversations(self, user: UserEntity) -> List[ConversationEntity]:
        return self.sql_service.get_user_conversations(user_id=user.id)

    def get_conversation(self, user: UserEntity, conversation_id: str) -> dict:
        doc = self.mongo_repo.get_conversation_by_id(conversation_id, str(user.id))

        if not doc:
            raise SentraHTTPException(
                status_code=404,
                code="CONVERSATION_NOT_FOUND",
                message="Conversation not found.",
                details=f"No conversation found with ID {conversation_id}",
                path=f"/conversations/{conversation_id}",
                suggestion="Check the conversation ID and try again."
            )
        return doc

    def update_conversation(self, user: UserEntity, conversation_id: str, request: UpdateConversationRequest) -> ConversationEntity:
        try:
            updated_sql = self.sql_service.update_conversation(
                conversation_id=conversation_id,
                title=request.title,
                description=request.description
            )

            result = self.mongo_repo.get_conversations_collection().update_one(
                {"_id": conversation_id, "user_id": str(user.id)},
                {"$set": request.dict(exclude_unset=True)}
            )

            if result.matched_count == 0:
                raise SentraHTTPException(
                    status_code=404,
                    code="CONVERSATION_NOT_FOUND",
                    message="Conversation not found in MongoDB.",
                    details=f"Update failed for conversation {conversation_id}",
                    path=f"/conversations/{conversation_id}",
                    suggestion="Check the conversation ID and try again."
                )

            return updated_sql

        except Exception as e:
            logger.error(f"Failed to update conversation {conversation_id}: {str(e)}")
            raise SentraHTTPException(
                status_code=500,
                code="UPDATE_FAILED",
                message="Failed to update the conversation.",
                details=str(e),
                path=f"/conversations/{conversation_id}"
            )

    def delete_conversation(self, user: UserEntity, conversation_id: str) -> None:
        sql_deleted = False
        mongo_deleted = False

        try:
            conversation = self.sql_service.get_conversation(conversation_id)
            if not conversation or str(conversation.user_id) != str(user.id):
                raise SentraHTTPException(
                    status_code=404,
                    code="CONVERSATION_NOT_FOUND",
                    message="Conversation not found.",
                    details=f"No conversation found with ID {conversation_id} for user {user.id}",
                    path=f"/conversations/{conversation_id}",
                    suggestion="Check the conversation ID and try again."
                )
            self.sql_service.delete_conversation(conversation_id)
            sql_deleted = True
        except Exception as e:
            logger.error(f"Failed to delete conversation {conversation_id} from SQL: {str(e)}")
            pass  

        try:
            result = self.mongo_repo.get_conversations_collection().delete_one({
                "_id": conversation_id,
                "user_id": str(user.id)
            })
            mongo_deleted = result.deleted_count > 0
        except Exception as e:
            logger.error(f"Failed to delete conversation {conversation_id} from MongoDB: {str(e)}")
            pass

        if not sql_deleted and not mongo_deleted:
            raise SentraHTTPException(
                status_code=404,
                code="CONVERSATION_NOT_FOUND",
                message="Conversation not found in both SQL and NoSQL.",
                details=f"No conversation found with ID {conversation_id}",
                path=f"/conversations/{conversation_id}",
                suggestion="Check the conversation ID and try again."
            )
