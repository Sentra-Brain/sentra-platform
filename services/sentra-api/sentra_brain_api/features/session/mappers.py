# sentra_brain_api/features/conversation/mappers.py

from sentra_core.domain.entities.session_entity import SessionEntity

from sentra_brain_api.features.session.schemas import (
    CreateSessionResponse,
    EventResponse,
    SessionListItemResponse,
    SessionResponse,
)


def entity_to_list_item_response(entity: SessionEntity) -> SessionListItemResponse:
    return SessionListItemResponse(
        id=entity.id, title=entity.title or "Untitled", created_at=entity.created_at
    )


def entity_to_creation_response(entity: SessionEntity) -> CreateSessionResponse:
    return CreateSessionResponse(
        id=entity.id, title=entity.title or "Untitled", created_at=entity.created_at
    )


def mongo_doc_to_response(doc: dict) -> SessionResponse:
    return SessionResponse(
        id=str(doc.get("_id")),
        title=doc.get("title"),
        description=doc.get("description"),
        initial_prompt=doc.get("initial_prompt"),
        created_at=doc.get("created_at"),
        updated_at=doc.get("updated_at"),
        events=[EventResponse(**evt) for evt in doc.get("events", [])],
    )
