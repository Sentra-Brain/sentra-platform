from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from sentra_brain_api.crosscutting.authorization import get_authenticated_user
from sentra_brain_api.features.conversation.api_service import ConversationApiService
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
from sentra.domain.entities.user_entity import UserEntity
from sentra.infra.nosql.conversation_mongo_repository import ConversationMongoRepository, get_conversation_mongo_repository
from sentra.infra.sql.postgres_service import get_db
from sentra.shared.logging import get_logger


logger = get_logger("sentra_brain_api.conversation")


class ConversationController:
	def __init__(self):
		self.router = APIRouter()
		self._add_routes()

	def _get_service(
		self,
		db: Session = Depends(get_db),
		
        mongo_repo: ConversationMongoRepository = Depends(get_conversation_mongo_repository)
	) -> ConversationApiService:
		return ConversationApiService(
			db=db,
			mongo_repo=mongo_repo
		)

	def _add_routes(self):
		@self.router.post(
			"/",
			response_model=CreateConversationResponse,
			description="Creates a new conversation for the current user",
		)
		async def create_conversation(
			body: CreateConversationRequest,
			current_user: UserEntity = Depends(get_authenticated_user),
			service: ConversationApiService = Depends(self._get_service),
		):
			return await service.create_conversation(current_user, body)

		@self.router.patch(
			"/{conversation_id}/title",
			response_model=UpdateConversationResponse,
			description="Generate or update conversation title using TitleAgent",
		)
		async def generate_title_for_conversation(
			conversation_id: UUID,
			current_user: UserEntity = Depends(get_authenticated_user),
			service: ConversationApiService = Depends(self._get_service),
		):
			return await service.generate_title_for_conversation(current_user, conversation_id)

		@self.router.get(
			"/",
			response_model=list[ConversationListItemResponse],
			description="Retrieves all conversations for the current user",
		)
		def get_conversations(
			current_user: UserEntity = Depends(get_authenticated_user),
			service: ConversationApiService = Depends(self._get_service),
		):
			return service.list_user_conversations(current_user)

		@self.router.get(
			"/{conversation_id}",
			response_model=ConversationResponse,
			description="Retrieve a specific conversation by its ID",
		)
		def get_conversation_by_id(
			conversation_id: UUID,
			current_user: UserEntity = Depends(get_authenticated_user),
			service: ConversationApiService = Depends(self._get_service),
		):
			return service.get_conversation(current_user, conversation_id)

		@self.router.put(
			"/{conversation_id}",
			response_model=UpdateConversationResponse,
			description="Update title and description of a conversation",
		)
		def update_conversation(
			conversation_id: UUID,
			request: UpdateConversationRequest,
			current_user: UserEntity = Depends(get_authenticated_user),
			service: ConversationApiService = Depends(self._get_service),
		):
			return service.update_conversation(current_user, conversation_id, request)

		@self.router.delete(
			"/{conversation_id}",
			response_model=DeleteConversationResponse,
			description="Delete a conversation",
		)
		def delete_conversation(
			conversation_id: UUID,
			current_user: UserEntity = Depends(get_authenticated_user),
			service: ConversationApiService = Depends(self._get_service),
		):
			return service.delete_conversation(current_user, conversation_id)

		@self.router.get(
			"/{conversation_id}/events",
			response_model=list[ResponseStreamEvent],
			description="Retrieve events for the conversation",
		)
		def get_events(
			conversation_id: UUID,
			since: datetime | None = Query(None),
			current_user: UserEntity = Depends(get_authenticated_user),
			service: ConversationApiService = Depends(self._get_service),
		):
			return service.get_events(current_user, conversation_id, since)

		@self.router.post(
			"/{conversation_id}/state",
			response_model=UpdateConversationStateResponse,
			description="Update conversation state",
		)
		def update_state(
			conversation_id: UUID,
			body: UpdateConversationStateRequest,
			current_user: UserEntity = Depends(get_authenticated_user),
			service: ConversationApiService = Depends(self._get_service),
		):
			return service.update_state(current_user, conversation_id, body)
