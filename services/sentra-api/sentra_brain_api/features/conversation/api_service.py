import asyncio
from datetime import datetime, timezone
from uuid import UUID
from sqlalchemy.orm import Session

from sentra.domain.entities.conversation_entity import ConversationEntity
from sentra.domain.entities.user_entity import UserEntity
from sentra.domain.services.conversation_service import ConversationService
from sentra.infra.nosql.conversation_mongo_repository import ConversationMongoRepository
from sentra.infra.sql.repositories.conversation_repository_sql import ConversationRepositorySql
from sentra.runtime.models import conversation
from sentra.shared.logging import get_logger
from sentra.runtime.agents.registry import agent_registry

from sentra_brain_api.core.exceptions import SentraHTTPException
from sentra_brain_api.features.conversation.mappers import (
    entity_to_creation_response,
    entity_to_list_item_response,
    entity_to_response,
)
from sentra_brain_api.features.conversation.schemas import (
    CreateConversationRequest,
    CreateConversationResponse,
    DeleteConversationResponse,
    ResponseStreamEvent,
    ConversationListItemResponse,
    ConversationResponse,
    UpdateConversationRequest,
    UpdateConversationResponse,
    UpdateConversationStateRequest,
    UpdateConversationStateResponse,
)

logger = get_logger("conversation_api_service")

class ConversationApiService:
    def __init__(self, db: Session, mongo_repo: ConversationMongoRepository):
        self.service = ConversationService(
            sql_repo=ConversationRepositorySql(db),
            nosql_repo=mongo_repo
            )

    async def create_conversation(
        self, user: UserEntity, request: CreateConversationRequest
    ) -> CreateConversationResponse:
        # 1. Create base conversation (no title yet)
        conversation = ConversationEntity(
            created_by_id=user.id,
            title="Untitled",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        conversation = self.service.create_conversation(user=user, conversation=conversation)

        # 2. If there’s an initial prompt, schedule title generation in background
        if request.initial_prompt:
            async def _generate_initial_title(conv_id: UUID, prompt: str):
                try:
                    from sentra.runtime.agents.registry import agent_registry
                    logger.info(f"[Async] Generating initial title for conversation {conv_id}...")
                    template = agent_registry.get("title_generator")

                    title_agent = template.build(
                        user_id="abc123",
                        conversation_id=None,
                        persist=False,
                    )
                    result = await title_agent.run([prompt], store=False)  # also tell provider not to store
                    title = getattr(result, "text", None) or str(result)
                    if title:
                        self.service.update_title(conv_id, title)
                        logger.info(f"[Async] Title updated for {conv_id}: {title}")
                except Exception as e:
                    logger.error(f"[Async] Failed to generate title for {conv_id}: {e}")

            asyncio.create_task(_generate_initial_title(conversation.id, request.initial_prompt))


        # 3. Return immediately — the frontend needs the conversation ID
        return entity_to_creation_response(conversation)

    async def generate_title_for_conversation(
        self, user: UserEntity, conversation_id: UUID
    ) -> UpdateConversationResponse:
        doc = self.service.get_conversation(conversation_id, user.id)
        if not doc:
            raise SentraHTTPException(status_code=404, details="Conversation not found")

        conversation =  ConversationResponse.from_mongo(doc)

        # Use first user + assistant messages as context
        first_user_event = next((e for e in conversation.messages if e.role == "user"), None)
        first_assistant_event = next((e for e in conversation.messages if e.role == "assistant"), None)
        if not first_user_event:
            raise ValueError("Cannot generate title: missing user event")
        # TODO: implement title generation here
        title = None
        # messages = [first_user_event.content]
        # if first_assistant_event and first_assistant_event.content:
        #     messages.append(first_assistant_event.content)

        # try:
        #     title_agent = agent_registry.get("title_generator").build(
        #         user_id=str(user.id),
        #         conversation_id=None,  # EPHEMERAL
        #         persist=False,
        #     )
        #     result = await title_agent.run(messages)
        #     title = getattr(result, "text", str(result))
        # except Exception as e:
        #     logger.error(f"Failed to generate title for conversation {conversation_id}: {e}")
        #     raise SentraHTTPException(status_code=500, details="Title generation failed")

        if title:
            self.service.update_title(conversation_id, title)
            conversation.title = title

        return UpdateConversationResponse(
            conversation_id=conversation_id,
            title=conversation.title,
            description=conversation.description,
        )

    def list_user_conversations(self, user: UserEntity) -> list[ConversationListItemResponse]:
        conversations = self.service.get_user_conversations(user.id)
        return [
            entity_to_list_item_response(conv) 
            for conv in conversations
        ]

    def get_conversation(
            self, user: UserEntity, conversation_id: UUID
            ) -> ConversationResponse:
        entity = self.service.get_conversation(conversation_id, user.id)
        if not entity:
            raise SentraHTTPException(status_code=404, details="Conversation not found")
        conversation =  ConversationResponse.from_mongo(entity)
        return conversation

    def update_conversation(
        self, conversation_id: UUID, req: UpdateConversationRequest
    ) -> UpdateConversationResponse:
        updated = self.service.update_conversation(
            conversation_id=conversation_id,
            title=req.title,
            description=req.description,
        )
        if not updated:
            raise SentraHTTPException(
                status_code=404,
                details="Conversation not found"
            )

        return UpdateConversationResponse(
            conversation_id=conversation_id,
            title=updated.title,
            description=updated.description,
        )

    def delete_conversation(
        self, user: UserEntity, conversation_id: UUID
    ) -> DeleteConversationResponse:
        deleted = self.service.delete_conversation(conversation_id, user.id)

        if not deleted:
            raise SentraHTTPException(
                status_code=404,
                details="Conversation not found"
            )
        
        return DeleteConversationResponse(success=True, message="Conversation deleted successfully")

    def get_events(
        self, user: UserEntity, conversation_id: UUID, since: datetime | None
    ) -> list[ResponseStreamEvent]:
        entity = self.service.get_conversation(conversation_id, user.id)

        if not entity:
            raise SentraHTTPException(
                status_code=404,
                details="Conversation not found"
            )
        
        conversation = entity_to_response(entity)
        events = conversation.messages
        if since:
            events = [e for e in events if e.timestamp > since]
        return events

    def update_state(
        self, user: UserEntity, conversation_id: UUID, req: UpdateConversationStateRequest
    ) -> UpdateConversationStateResponse:
        updated = self.service.update_state(conversation_id, user.id, req.state)

        if not updated:
            raise SentraHTTPException(
                status_code=404,
                details="Conversation not found"
            )
        
        return UpdateConversationStateResponse(conversation_id=conversation_id, state=req.state)
