# packages/sentra-domain/src/sentra/domain/enums/document.py
import enum

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
    TO_BE_REMOVED = "to_be_removed"
    REMOVED = "removed"
