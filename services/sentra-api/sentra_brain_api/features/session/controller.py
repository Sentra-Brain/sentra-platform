from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from sentra_brain_api.crosscutting.authorization import get_authenticated_user
from sentra_brain_api.features.session.api_service import SessionApiService
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
from sentra.domain.entities.user_entity import UserEntity
from sentra.infra.nosql.mongo_session_repository import (
    MongoSessionRepository,
    get_session_mongo_repository,
)
from sentra.infra.sql.postgres_service import get_db
from sentra.shared.logging import get_logger

logger = get_logger("sentra_brain_api.session")


class SessionController:
    def __init__(self):
        self.router = APIRouter()
        self._add_routes()

    def _get_service(
        self,
        db: Session = Depends(get_db),
        mongo_repo: MongoSessionRepository = Depends(get_session_mongo_repository),
    ) -> SessionApiService:
        return SessionApiService(db=db, mongo_repo=mongo_repo)

    def _add_routes(self):
        @self.router.post(
            "/",
            response_model=CreateSessionResponse,
            description="Creates a new session for the current user",
        )
        async def create_session(
            body: CreateSessionRequest,
            current_user: UserEntity = Depends(get_authenticated_user),
            service: SessionApiService = Depends(self._get_service),
        ):
            return await service.create_session(current_user, body)

        @self.router.patch(
            "/{session_id}/title",
            response_model=UpdateSessionResponse,
            description="Generate or update session title using TitleAgent",
        )
        async def generate_title_for_session(
            session_id: UUID,
            current_user: UserEntity = Depends(get_authenticated_user),
            service: SessionApiService = Depends(self._get_service),
        ):
            return await service.generate_title_for_session(current_user, session_id)

        # Backwards-compatible alias
        @self.router.post(
            "/{session_id}/generate-title",
            response_model=UpdateSessionResponse,
            include_in_schema=False,
        )
        async def legacy_generate_title(
            session_id: UUID,
            current_user: UserEntity = Depends(get_authenticated_user),
            service: SessionApiService = Depends(self._get_service),
        ):
            return await service.generate_title_for_session(current_user, session_id)

        @self.router.get(
            "/",
            response_model=list[SessionListItemResponse],
            description="Retrieves all sessions for the current user",
        )
        def get_sessions(
            current_user: UserEntity = Depends(get_authenticated_user),
            service: SessionApiService = Depends(self._get_service),
        ):
            return service.list_user_sessions(current_user)

        @self.router.get(
            "/{session_id}",
            response_model=SessionResponse,
            description="Retrieve a specific session by its ID",
        )
        def get_session_by_id(
            session_id: UUID,
            current_user: UserEntity = Depends(get_authenticated_user),
            service: SessionApiService = Depends(self._get_service),
        ):
            return service.get_session(current_user, session_id)

        @self.router.put(
            "/{session_id}",
            response_model=UpdateSessionResponse,
            description="Update title and description of a session",
        )
        def update_session(
            session_id: UUID,
            request: UpdateSessionRequest,
            current_user: UserEntity = Depends(get_authenticated_user),
            service: SessionApiService = Depends(self._get_service),
        ):
            return service.update_session(current_user, session_id, request)

        @self.router.delete(
            "/{session_id}",
            response_model=DeleteSessionResponse,
            description="Delete a session",
        )
        def delete_session(
            session_id: UUID,
            current_user: UserEntity = Depends(get_authenticated_user),
            service: SessionApiService = Depends(self._get_service),
        ):
            return service.delete_session(current_user, session_id)

        @self.router.get(
            "/{session_id}/events",
            response_model=list[EventResponse],
            description="Retrieve events for the session",
        )
        def get_events(
            session_id: UUID,
            since: datetime | None = Query(None),
            current_user: UserEntity = Depends(get_authenticated_user),
            service: SessionApiService = Depends(self._get_service),
        ):
            return service.get_events(current_user, session_id, since)

        @self.router.post(
            "/{session_id}/state",
            response_model=UpdateSessionStateResponse,
            description="Update session state",
        )
        def update_state(
            session_id: UUID,
            body: UpdateSessionStateRequest,
            current_user: UserEntity = Depends(get_authenticated_user),
            service: SessionApiService = Depends(self._get_service),
        ):
            return service.update_state(current_user, session_id, body)
    