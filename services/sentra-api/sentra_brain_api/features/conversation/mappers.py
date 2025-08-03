# sentra_brain_api/features/conversation/mappers.py

from sentra_core.domain.entities.conversation_entity import ConversationEntity
from sentra_brain_api.features.conversation.schemas import (
    ConversationListItemResponse,
    ConversationResponse,
    CreateConversationResponse,
    MessageResponse
)

def entity_to_list_item_response(entity: ConversationEntity) -> ConversationListItemResponse:
    return ConversationListItemResponse(
        id=str(entity.id),
        title=entity.title or "Untitled",
        created_at=entity.created_at
    )

def entity_to_creation_response(entity: ConversationEntity) -> CreateConversationResponse:
    return CreateConversationResponse(
        id=str(entity.id),
        title=entity.title or "Untitled",
        created_at=entity.created_at
    )

def mongo_doc_to_response(doc: dict) -> ConversationResponse:
    return ConversationResponse(
        id=str(doc.get("_id")),
        title=doc.get("title"),
        description=doc.get("description"),
        initial_prompt=doc.get("initial_prompt"),
        created_at=doc.get("created_at"),
        updated_at=doc.get("updated_at"),
        messages=[
            MessageResponse(**msg) for msg in doc.get("messages", [])
        ]
    )
