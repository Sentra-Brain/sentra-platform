from sentra.domain.entities.conversation_entity import ConversationEntity
from sentra_brain_api.features.conversation.schemas import (
	CreateConversationResponse,
	EventResponse,
	ConversationListItemResponse,
	ConversationResponse,
)

def entity_to_response(entity: ConversationEntity) -> ConversationResponse:
	return ConversationResponse(
		id=entity.id,
		title=entity.title or "Untitled",
		description=entity.description,
		initial_prompt=getattr(entity, "initial_prompt", None),
		created_at=entity.created_at,
		updated_at=getattr(entity, "updated_at", None),
		events=[EventResponse(**event) if isinstance(event, dict) else event for event in getattr(entity, "events", [])],
	)

def entity_to_list_item_response(entity: ConversationEntity) -> ConversationListItemResponse:
	return ConversationListItemResponse(
		id=entity.id, title=entity.title or "Untitled", created_at=entity.created_at
	)

def entity_to_creation_response(entity: ConversationEntity) -> CreateConversationResponse:
	return CreateConversationResponse(
		id=entity.id, title=entity.title or "Untitled", created_at=entity.created_at
	)

