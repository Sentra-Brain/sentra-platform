# sentra_brain_api/features/knowledge/schemas.py

from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field
from sentra.domain.entities.knowledge_source_entity import KnowledgeSourceType, KnowledgeSourceVisibility, KnowledgeSourceStatus
from sentra.domain.entities.document_entity import DocumentFileType, DocumentStatus
from sentra_brain_api.shared_models.user_refs import UserRef


# Knowledge Source Schemas
class CreateKnowledgeSourceRequest(BaseModel):
    name: str = Field(..., description="Human-friendly name for the source")
    type: KnowledgeSourceType = Field(..., description="Type of knowledge source")
    path: Optional[str] = Field(None, description="File path for folder-type sources")
    description: Optional[str] = Field(None, description="Optional source description")
    visibility: KnowledgeSourceVisibility = Field(KnowledgeSourceVisibility.PRIVATE, description="Source visibility")
    auto_index: bool = Field(False, description="Whether to automatically scan and index")


class KnowledgeSourceResponse(BaseModel):
    id: UUID
    name: str
    type: KnowledgeSourceType
    path: Optional[str] = None
    description: Optional[str] = None
    created_by: UserRef
    created_at: datetime
    visibility: KnowledgeSourceVisibility
    auto_index: bool
    status: KnowledgeSourceStatus

    model_config = {
        "from_attributes": True,
        "populate_by_name": True
    }


# Document Schemas
class DocumentUploadRequest(BaseModel):
    display_name: str = Field(..., description="User-defined document name")
    description: Optional[str] = Field(None, description="Optional document description")


class DocumentResponse(BaseModel):
    id: UUID
    filename: str
    display_name: str
    description: Optional[str] = None
    filetype: DocumentFileType
    path: str
    created_by: UserRef
    created_at: datetime
    status: DocumentStatus
    status_message: Optional[str] = None
    error: Optional[str] = None
    chunks_count: Optional[int] = None
    knowledge_source_id: UUID
    has_markdown: bool = False

    model_config = {
        "from_attributes": True,
        "populate_by_name": True
    }


class DocumentMarkdownResponse(BaseModel):
    document_id: UUID
    markdown: str

# List responses
class KnowledgeSourceListResponse(BaseModel):
    sources: List[KnowledgeSourceResponse]
    total: int

    model_config = {
        "from_attributes": True,
        "populate_by_name": True
    }


class DocumentListResponse(BaseModel):
    documents: List[DocumentResponse]
    total: int

    model_config = {
        "from_attributes": True,
        "populate_by_name": True
    }