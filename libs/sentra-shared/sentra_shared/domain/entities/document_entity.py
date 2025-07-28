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
    HTML = "html"
    EML = "eml"
    MSG = "msg"
    EPUB = "epub"


class DocumentStatus(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    EXTRACTING = "extracting"
    CHUNKING = "chunking"
    EMBEDDING = "embedding"
    INDEXING = "indexing"
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
    status = Column(Enum(DocumentStatus), nullable=False, default=DocumentStatus.PENDING)
    status_message = Column(Text, nullable=True)
    error = Column(Text, nullable=True)
    chunks_count = Column(Integer, nullable=True)
    knowledge_source_id = Column(UUID(as_uuid=True), ForeignKey("knowledge_sources.id"), nullable=False)