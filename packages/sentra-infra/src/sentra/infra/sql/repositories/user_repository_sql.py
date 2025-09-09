# packages/sentra-infra/src/sentra/infra/sql/repositories/user_repository_sql.py
from sqlalchemy.orm import Session
from sentra.domain.entities.user_entity import UserEntity
from sentra.domain.repository.user_repository import IUserRepository
from sentra.infra.sql.repositories.base_repository import BaseRepository
from typing import Optional

class UserRepositorySql(BaseRepository[UserEntity], IUserRepository):
    def __init__(self, db: Session):
        super().__init__(UserEntity, db)

    def get_by_username(self, username: str) -> Optional[UserEntity]:
        return self.db.query(UserEntity).filter(UserEntity.username == username, UserEntity.deleted_at.is_(None)).first()

    def get_by_email(self, email: str) -> Optional[UserEntity]:
        return self.db.query(UserEntity).filter(UserEntity.email == email, UserEntity.deleted_at.is_(None)).first()
