# sentra_shared/domain/knowledge_source_entity.py

from sqlalchemy import Text, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import ENUM as PgEnum, UUID
from sentra_shared.domain.entities.base_entity import BaseEntity
from sentra_shared.domain.enums.knowledge import (
    KnowledgeSourceStatus,
    KnowledgeSourceType,
    KnowledgeSourceVisibility,
)


class KnowledgeSourceEntity(BaseEntity):
    __tablename__ = "knowledge_sources"

    name: Mapped[str] = mapped_column(Text, nullable=False)

    type: Mapped[KnowledgeSourceType] = mapped_column(
        PgEnum(KnowledgeSourceType, name="knowledge_source_type", metadata=BaseEntity.metadata),
        nullable=False
    )

    path: Mapped[str | None] = mapped_column(Text, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    visibility: Mapped[KnowledgeSourceVisibility] = mapped_column(
        PgEnum(KnowledgeSourceVisibility, name="knowledge_source_visibility", metadata=BaseEntity.metadata),
        nullable=False,
        default=KnowledgeSourceVisibility.PRIVATE
    )

    auto_index: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    status: Mapped[KnowledgeSourceStatus] = mapped_column(
        PgEnum(KnowledgeSourceStatus, name="knowledge_source_status", metadata=BaseEntity.metadata),
        nullable=False,
        default=KnowledgeSourceStatus.ACTIVE
    )

    # Relationships
    created_by_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_by = relationship("UserEntity", back_populates="knowledge_sources", lazy="joined")
