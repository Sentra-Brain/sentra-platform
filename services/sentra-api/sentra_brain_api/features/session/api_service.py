from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from sentra_core.domain.entities.session_entity import SessionEntity
from sentra_core.domain.entities.user_entity import UserEntity
from sentra_core.domain.repository.session_repository import SessionRepository
from sentra_core.domain.services.session_service import SessionService
from sentra_core.infra.nosql.mongo_session_repository import MongoSessionRepository
from sentra_core.logging import get_logger

from sentra_brain_api.core.exceptions import SentraHTTPException
from sentra_brain_api.features.session.mappers import (
    entity_to_creation_response,
    entity_to_list_item_response,
    mongo_doc_to_response,
)
from sentra_brain_api.features.session.schemas import (
    CreateSessionRequest,
    CreateSessionResponse,
    DeleteSessionResponse,
    EventResponse,
    SessionListItemResponse,
    SessionResponse,
    UpdateSessionRequest,
    UpdateSessionResponse,
    UpdateSessionStateRequest,
    UpdateSessionStateResponse,
)
from sentra_brain_api.features.session.title.title_generation_service import (
    TitleGenerationService,
)

logger = get_logger("session_api_service")


class SessionApiService:
    def __init__(self, db: Session, mongo_repo: MongoSessionRepository):
        self.service = SessionService(
            sql_repo=SessionRepository(db), mongo_repo=mongo_repo
        )
        self.title_service = TitleGenerationService()

    async def create_session(
        self, user: UserEntity, request: CreateSessionRequest
    ) -> CreateSessionResponse:
        try:
            title = self.title_service.generate_initial_title(request.initial_prompt)
        except Exception as e:
            logger.warning(f"Failed to generate initial title: {e}")
            title = None

        session = SessionEntity(
            created_by_id=user.id,
            title=title,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        session = self.service.create_session(user=user, session=session)

        return entity_to_creation_response(session)

    async def generate_llm_title_for_session(
        self, user: UserEntity, session_id: UUID
    ) -> UpdateSessionResponse:
        doc = self.service.get_session(session_id, user.id)
        if not doc:
            raise SentraHTTPException(
                status_code=404,
                details="Session not found",
            )

        session = mongo_doc_to_response(doc)

        # Find the first user event to use as the prompt
        first_user_event = next((e for e in session.events if e.role == "user"), None)
        if not first_user_event:
            raise ValueError("Cannot generate LLM title: missing user event")

        title = await self.title_service.generate_llm_title(first_user_event.content)
        if title:
            self.service.update_title(session_id, user.id, title)
            session.title = title

        return UpdateSessionResponse(
            session_id=session_id,
            title=session.title,
            description=session.description,
        )

    def list_user_sessions(self, user: UserEntity) -> list[SessionListItemResponse]:
        sessions = self.service.get_user_sessions(user.id)
        return [entity_to_list_item_response(sess) for sess in sessions]

    def get_session(self, user: UserEntity, session_id: UUID) -> SessionResponse:
        doc = self.service.get_session(session_id, user.id)
        if not doc:
            raise SentraHTTPException(
                status_code=404,
                details="Session not found",
            )
        return mongo_doc_to_response(doc)

    def update_session(
        self, user: UserEntity, session_id: UUID, req: UpdateSessionRequest
    ) -> UpdateSessionResponse:
        updated = self.service.update_session(
            session_id=session_id,
            user_id=user.id,
            title=req.title,
            description=req.description,
        )

        if not updated:
            raise SentraHTTPException(
                status_code=404,
                details="Session not found",
            )

        return UpdateSessionResponse(
            session_id=session_id,
            title=updated.title,
            description=updated.description,
        )

    def delete_session(
        self, user: UserEntity, session_id: UUID
    ) -> DeleteSessionResponse:
        deleted = self.service.delete_session(session_id, user.id)

        if not deleted:
            raise SentraHTTPException(
                status_code=404,
                details="Session not found",
            )

        return DeleteSessionResponse(
            success=True, message="Session deleted successfully"
        )

    def get_events(
        self, user: UserEntity, session_id: UUID, since: datetime | None
    ) -> list[EventResponse]:
        doc = self.service.get_session(session_id, user.id)
        if not doc:
            raise SentraHTTPException(
                status_code=404,
                details="Session not found",
            )
        session = mongo_doc_to_response(doc)
        events = session.events
        if since:
            events = [e for e in events if e.timestamp > since]
        return events

    def update_state(
        self, user: UserEntity, session_id: UUID, req: UpdateSessionStateRequest
    ) -> UpdateSessionStateResponse:
        updated = self.service.update_state(session_id, user.id, req.state)
        if not updated:
            raise SentraHTTPException(
                status_code=404,
                details="Session not found",
            )
        return UpdateSessionStateResponse(session_id=session_id, state=req.state)
