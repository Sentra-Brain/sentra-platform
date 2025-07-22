# sentra_brain_api/domain/user_entity.py
from typing import List
from sqlalchemy import String, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sentra_brain_api.domain.base_entity import BaseEntity
from sentra_brain_api.domain.role import Role

class UserEntity(BaseEntity):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String)
    hashed_password: Mapped[str] = mapped_column(String)
    disabled: Mapped[bool] = mapped_column(Boolean, default=False)
    roles: Mapped[str] = mapped_column(String)  # CSV format

    conversations = relationship("ConversationEntity", back_populates="user", cascade="all, delete-orphan")

    def get_roles(self) -> List[Role]:
        return [Role(role.strip()) for role in self.roles.split(",") if role]

    def set_roles(self, roles: List[Role]) -> None:
        self.roles = ",".join(role.value for role in roles)
