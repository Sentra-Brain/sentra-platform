# sentra_shared/domain/services/user_service.py

from uuid import UUID
from typing import Optional
from sentra_shared.domain.entities.user_entity import UserEntity
from sentra_shared.domain.enums.role import Role
from sentra_shared.domain.repository.user_repository import UserRepository
from sentra_shared.domain.entities.system_settings import SystemSettingsEntity
from sqlalchemy.orm import Session


class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def get_user_by_username(self, username: str) -> Optional[UserEntity]:
        return self.user_repo.get_by_username(username)

    def get_user_by_id(self, user_id: UUID) -> Optional[UserEntity]:
        return self.user_repo.get(user_id)

    def get_user_display_name(self, user_id: UUID) -> str:
        user = self.user_repo.get(user_id)
        if not user:
            raise ValueError("User not found")
        return user.full_name or user.username or user.email

    def create_user(self, username: str, email: str, full_name: str, hashed_password: str) -> UserEntity:
        user = UserEntity(
            username=username,
            email=email,
            full_name=full_name,
            hashed_password=hashed_password,
            disabled=True
        )
        user.set_roles([Role.USER])
        self.user_repo.create(user)
        return user

    def enable_user(self, user_id: UUID) -> Optional[UserEntity]:
        user = self.user_repo.get(user_id)
        if user:
            user.disabled = False
            self.user_repo.update(user)
        return user

    def update_user(self, user_id: UUID, full_name: Optional[str], email: Optional[str], hashed_password: Optional[str]) -> Optional[UserEntity]:
        user = self.user_repo.get(user_id)
        if not user:
            return None
        if full_name:
            user.full_name = full_name
        if email:
            user.email = email
        if hashed_password:
            user.hashed_password = hashed_password
        self.user_repo.update(user)
        return user

    def get_max_user_limit(self) -> int:
        settings = self.db.query(SystemSettingsEntity).first()
        return settings.max_users if settings else -1

    def count_non_superadmin_users(self) -> int:
        return self.db.query(UserEntity).filter(~UserEntity.roles.contains("superadmin")).count()
