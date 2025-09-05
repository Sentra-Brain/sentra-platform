from uuid import UUID
from sqlalchemy.orm import Session
from sentra.domain.entities.user_entity import UserEntity
from sentra.domain.repository.base_repository import BaseRepository


class UserRepository(BaseRepository[UserEntity]):
    def __init__(self, db: Session):
        super().__init__(UserEntity, db)

    def get_by_username(self, username: str) -> UserEntity | None:
        return self.db.query(UserEntity).filter(UserEntity.username == username, UserEntity.deleted_at.is_(None)).first()

    def get_by_email(self, email: str) -> UserEntity | None:
        return self.db.query(UserEntity).filter(UserEntity.email == email, UserEntity.deleted_at.is_(None)).first()
