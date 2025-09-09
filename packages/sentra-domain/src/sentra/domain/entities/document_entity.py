# packages/sentra-domain/src/sentra/domain/entities/document_entity.py

from sqlalchemy import Boolean, String, Text, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import ENUM as PgEnum, UUID
from sentra.domain.entities.base_entity import BaseEntity
from sentra.domain.enums.document import DocumentFileType, DocumentStatus


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

    markdown_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    markdown_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    markdown_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    has_markdown: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    
    # Relationships
    knowledge_source_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("knowledge_sources.id"), nullable=False)
    created_by_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_by = relationship("UserEntity", back_populates="documents", lazy="joined")
