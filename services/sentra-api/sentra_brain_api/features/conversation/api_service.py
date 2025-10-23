from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from sentra.domain.entities.conversation_entity import ConversationEntity
from sentra.domain.entities.user_entity import UserEntity
from sentra.domain.services.conversation_service import ConversationService
from sentra.infra.sql.repositories.conversation_repository_sql import ConversationRepositorySql
from sentra.runtime.agents.title_agent import TitleAgent
from sentra.shared.logging import get_logger

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
	EventResponse,
	ConversationListItemResponse,
	ConversationResponse,
	UpdateConversationRequest,
	UpdateConversationResponse,
	UpdateConversationStateRequest,
	UpdateConversationStateResponse,
)

logger = get_logger("conversation_api_service")


class ConversationApiService:
	def __init__(self, db: Session):
		self.service = ConversationService(
			sql_repo=ConversationRepositorySql(db)
		)
		self.title_agent = TitleAgent()

	async def create_conversation(
		self, user: UserEntity, request: CreateConversationRequest
	) -> CreateConversationResponse:
		try:
			title = self.title_agent.generate_initial(request.initial_prompt)
		except Exception as e:
			logger.warning(f"Failed to generate initial title: {e}")
			title = None

		conversation = ConversationEntity(
			created_by_id=user.id,
			title=title,
			created_at=datetime.now(timezone.utc),
			updated_at=datetime.now(timezone.utc),
		)

		conversation = self.service.create_conversation(user=user, conversation=conversation)

		return entity_to_creation_response(conversation)

	async def generate_title_for_conversation(
		self, user: UserEntity, conversation_id: UUID
	) -> UpdateConversationResponse:
		entity = self.service.get_conversation(conversation_id)
		if not entity:
			raise SentraHTTPException(
				status_code=404,
				details="Conversation not found",
			)

		# Map entity to ConversationResponse (implement entity_to_response if needed)
		conversation = entity_to_response(entity)

		# Use first user and assistant messages as context
		first_user_event = next((e for e in conversation.events if e.role == "user"), None)
		first_assistant_event = next(
			(e for e in conversation.events if e.role == "assistant"), None
		)
		if not first_user_event:
			raise ValueError("Cannot generate title: missing user event")

		messages = [first_user_event.content]
		if first_assistant_event and first_assistant_event.content:
			messages.append(first_assistant_event.content)

		title = await self.title_agent.generate(messages)
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
		return [entity_to_list_item_response(conv) for conv in conversations]

	def get_conversation(self, conversation_id: UUID) -> ConversationResponse:
		entity = self.service.get_conversation(conversation_id)
		if not entity:
			raise SentraHTTPException(
				status_code=404,
				details="Conversation not found",
			)
		return entity_to_response(entity)

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
				details="Conversation not found",
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
				details="Conversation not found",
			)

		return DeleteConversationResponse(
			success=True, message="Conversation deleted successfully"
		)

	def get_events(
		self, user: UserEntity, conversation_id: UUID, since: datetime | None
	) -> list[EventResponse]:
		entity = self.service.get_conversation(conversation_id)
		if not entity:
			raise SentraHTTPException(
				status_code=404,
				details="Conversation not found",
			)
		conversation = entity_to_response(entity)
		events = conversation.events
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
				details="Conversation not found",
			)
		return UpdateConversationStateResponse(conversation_id=conversation_id, state=req.state)
