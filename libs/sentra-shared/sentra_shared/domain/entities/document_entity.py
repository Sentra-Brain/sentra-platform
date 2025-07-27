# services/sentra-shared/sentra_shared/domain/document_entity.py
import enum
from sqlalchemy import Column, ForeignKey, Enum, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sentra_shared.domain.entities.base_entity import BaseEntity


class DocumentFileType(enum.Enum):
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    MD = "md"


class DocumentStatus(enum.Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    INDEXED = "indexed"
    FAILED = "failed"


class DocumentEntity(BaseEntity):
    __tablename__ = "documents"

    filename = Column(Text, nullable=False)
    display_name = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    filetype = Column(Enum(DocumentFileType), nullable=False)
    path = Column(Text, nullable=False)
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    status = Column(Enum(DocumentStatus), nullable=False, default=DocumentStatus.QUEUED)
    error = Column(Text, nullable=True)
    chunks_count = Column(Integer, nullable=True)
    knowledge_source_id = Column(UUID(as_uuid=True), ForeignKey("knowledge_sources.id"), nullable=False)