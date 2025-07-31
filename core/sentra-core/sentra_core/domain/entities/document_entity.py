# sentra_core/domain/document_entity.py

from sqlalchemy import Text, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import ENUM as PgEnum, UUID
from sentra_core.domain.entities.base_entity import BaseEntity
from sentra_core.domain.enums.document import DocumentFileType, DocumentStatus


class DocumentEntity(BaseEntity):
    __tablename__ = "documents"

    filename: Mapped[str] = mapped_column(Text, nullable=False)
    display_name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    filetype: Mapped[DocumentFileType] = mapped_column(
        PgEnum(DocumentFileType, name="document_file_type", metadata=BaseEntity.metadata),
        nullable=False
    )

    path: Mapped[str] = mapped_column(Text, nullable=False)

    status: Mapped[DocumentStatus] = mapped_column(
        PgEnum(DocumentStatus, name="document_status", metadata=BaseEntity.metadata),
        nullable=False,
        default=DocumentStatus.PENDING
    )

    status_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    chunks_count: Mapped[int | None] = mapped_column(Integer, nullable=True)

    knowledge_source_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("knowledge_sources.id"),
        nullable=False
    )

    # Relationships
    created_by_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_by = relationship("UserEntity", back_populates="documents", lazy="joined")
