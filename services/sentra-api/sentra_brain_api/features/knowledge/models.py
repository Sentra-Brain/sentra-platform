# sentra_brain_api/features/knowledge/schemas.py

from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field
from sentra_brain_api.domain.knowledge_source_entity import KnowledgeSourceType, KnowledgeSourceVisibility, KnowledgeSourceStatus
from sentra_brain_api.domain.document_entity import DocumentFileType, DocumentStatus


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
    created_by: UUID
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
    uploaded_by: UUID
    created_at: datetime
    status: DocumentStatus
    error: Optional[str] = None
    knowledge_source_id: UUID

    model_config = {
        "from_attributes": True,
        "populate_by_name": True
    }


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