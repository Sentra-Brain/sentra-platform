"""Repository for managing :class:`SessionEntity` records."""

from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from sentra.domain.entities.session_entity import SessionEntity
from sentra.domain.repository.base_repository import BaseRepository


class SessionRepository(BaseRepository[SessionEntity]):
    def __init__(self, db: Session):
        super().__init__(SessionEntity, db)

    def create_with_user_id(self, user_id: UUID) -> UUID:
        session_id = uuid4()
        session = SessionEntity(id=session_id, created_by_id=user_id)
        self.db.add(session)
        self.db.commit()
        return session_id

    def get_sessions_by_user_id(self, user_id: UUID):
        return self.db.query(SessionEntity).filter(SessionEntity.created_by_id == user_id).all()

    def update_title(self, session_id: UUID, title: str):
        session = self.get(session_id)
        if session:
            session.title = title
            self.db.commit()
        
