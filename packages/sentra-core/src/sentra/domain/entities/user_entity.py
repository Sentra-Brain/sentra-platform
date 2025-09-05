# sentra/domain/user_entity.py
from typing import List
from sqlalchemy import String, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sentra.domain.entities.base_entity import BaseEntity
from sentra.domain.enums.role import Role

class UserEntity(BaseEntity):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String)
    hashed_password: Mapped[str] = mapped_column(String)
    disabled: Mapped[bool] = mapped_column(Boolean, default=False)
    roles: Mapped[str] = mapped_column(String)
    job_title: Mapped[str] = mapped_column(String, nullable=True)
    avatar_url: Mapped[str] = mapped_column(String, nullable=True)
    phone_number: Mapped[str] = mapped_column(String, nullable=True)
    bio: Mapped[str] = mapped_column(String, nullable=True)
    preferred_language: Mapped[str] = mapped_column(String, default="es", nullable=False)
    timezone: Mapped[str] = mapped_column(String, default="Europe/Madrid", nullable=False)

    def get_roles(self) -> List[Role]:
        return [Role(role.strip()) for role in self.roles.split(",") if role]

    def set_roles(self, roles: List[Role]) -> None:
        self.roles = ",".join(role.value for role in roles)

    # Relationships
    sessions = relationship("SessionEntity", back_populates="created_by", cascade="all, delete-orphan")
    documents = relationship("DocumentEntity", back_populates="created_by", cascade="all, delete-orphan")
    knowledge_sources = relationship("KnowledgeSourceEntity", back_populates="created_by", cascade="all, delete-orphan")
