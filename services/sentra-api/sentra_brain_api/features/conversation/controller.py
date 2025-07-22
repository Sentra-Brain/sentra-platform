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
    ConversationListItemModel,
    ConversationModel,
    CreateConversationRequest,
    CreateConversationResponse,
    DeleteConversationResponse,
    UpdateConversationRequest,
    UpdateConversationResponse
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

                return CreateConversationResponse(conversation_id=str(conversation.id))
        
        @self.router.get(
            "/",
            response_model=list[ConversationListItemModel],
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
            conversation_repository: MongoConversationRepository = Depends(get_conversation_mongo_repository),
        ):
            logger.info(f"Retrieving conversation {conversation_id} for user {current_user.id}")

            # Fetch from MongoDB
            conversation_doc = conversation_repository.get_conversations_collection().find_one({"_id": conversation_id})

            if not conversation_doc:
                raise SentraHTTPException(
                    status_code=404,
                    code="CONVERSATION_NOT_FOUND",
                    message="Conversation not found.",
                    details=f"No conversation found with ID {conversation_id}",
                    path=f"/conversations/{conversation_id}",
                    suggestion="Check the conversation ID and try again."
                )

            # Convert to ConversationModel
            messages = [
                {
                    "role": msg["role"],
                    "content": msg["content"],
                    "timestamp": datetime.fromisoformat(msg["timestamp"])
                }
                for msg in conversation_doc.get("messages", [])
            ]

            return ConversationModel(
                conversation_id=conversation_id,
                title=conversation_doc.get("title"),
                description=conversation_doc.get("description"),
                initial_prompt=conversation_doc.get("initial_prompt"),
                created_at=datetime.fromisoformat(conversation_doc["created_at"]),
                updated_at=datetime.fromisoformat(conversation_doc.get("updated_at", datetime.now(timezone.utc).isoformat())),
                messages=messages
            )
            
        @self.router.put(
            "/{conversation_id}",
            response_model=ConversationModel,
            description="Update title and description of a conversation"
        )
        def update_conversation(
            conversation_id: str,
            request: UpdateConversationRequest,
            current_user: UserEntity = Depends(get_authenticated_user),
            mongo_repo: MongoConversationRepository = Depends(get_conversation_mongo_repository),
            db: Session = Depends(get_db)
        ):
            logger.info(f"Updating conversation {conversation_id} for user {current_user.id}")

            # SQL check + update
            sql_repo = ConversationRepository(db)
            service = ConversationService(sql_repo)
            conversation = service.get_conversation_by_id(conversation_id)

            if not conversation or str(conversation.user_id) != str(current_user.id):
                raise SentraHTTPException(
                    status_code=404,
                    code="CONVERSATION_NOT_FOUND",
                    message="Conversation not found.",
                    details=f"No conversation found with ID {conversation_id} for user {current_user.id}",
                    path=f"/conversations/{conversation_id}",
                    suggestion="Check the conversation ID and try again."
                )

            updated_sql = service.update_conversation(
                conversation_id=conversation_id,
                title=request.title,
                description=request.description
            )

            # Mongo update
            mongo_doc = mongo_repo.get_conversations_collection().find_one({"_id": conversation_id})
            if not mongo_doc:
                raise SentraHTTPException(
                    status_code=404,
                    code="CONVERSATION_NOT_FOUND",
                    message="Conversation not found.",
                    details=f"No conversation found with ID {conversation_id} in MongoDB",
                    path=f"/conversations/{conversation_id}",
                    suggestion="Check the conversation ID and try again."
                )

            update_fields = request.dict(exclude_unset=True)
            mongo_repo.get_conversations_collection().update_one(
                {"_id": conversation_id},
                {"$set": update_fields}
            )

            return UpdateConversationResponse(
                conversation_id=str(updated_sql.id),
                title=updated_sql.title,
                description=updated_sql.description,
            )

        @self.router.delete(
            "/{conversation_id}",
            response_model=DeleteConversationResponse,
            description="Delete a conversation"
        )
        def delete_conversation(
            conversation_id: str,
            current_user: UserEntity = Depends(get_authenticated_user),
            nosql_repo: MongoConversationRepository = Depends(get_conversation_mongo_repository),
            db: Session = Depends(get_db)
        ):
            sql_deleted = False
            nosql_deleted = False
            try:
                logger.info(f"Deleting conversation {conversation_id} for user {current_user.id}")

                # SQL check + delete
                sql_repo = ConversationRepository(db)
                service = ConversationService(sql_repo)
                conversation = service.get_conversation(conversation_id)

                if not conversation or str(conversation.user_id) != str(current_user.id):
                    raise SentraHTTPException(
                        status_code=404,
                        code="CONVERSATION_NOT_FOUND",
                        message="Conversation not found.",
                        details=f"No conversation found with ID {conversation_id} for user {current_user.id}",
                        path=f"/conversations/{conversation_id}",
                        suggestion="Check the conversation ID and try again."
                    )

                service.delete_conversation(conversation_id)
                logger.info(f"Deleted conversation {conversation_id} from SQL")
                sql_deleted = True
            except ValueError as e:
                logger.error(f"SQL delete failed: {str(e)}")
 
            # Mongo delete
            try:
                nosql_repo.get_conversations_collection().delete_one({"_id": conversation_id})
                nosql_deleted = True
                logger.info(f"Deleted conversation {conversation_id} from NoSQL")
            except Exception as e:
                logger.error(f"NoSQL delete failed: {str(e)}")

            if not sql_deleted and not nosql_deleted:
                raise SentraHTTPException(
                    status_code=404,
                    code="CONVERSATION_NOT_FOUND",
                    message="Conversation not found in both SQL nor NoSQL.",
                    details=f"No conversation found with ID {conversation_id}",
                    path=f"/conversations/{conversation_id}",
                    suggestion="Check the conversation ID and try again."
                )
            logger.info(f"Successfully deleted conversation {conversation_id} for user {current_user.id}")
            return DeleteConversationResponse(
                success=True,
                message="Conversation deleted successfully"
            )
