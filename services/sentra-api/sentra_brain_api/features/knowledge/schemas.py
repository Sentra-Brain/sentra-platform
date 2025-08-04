# sentra_brain_api/features/knowledge/schemas.py

from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field
from sentra_core.domain.entities.knowledge_source_entity import KnowledgeSourceType, KnowledgeSourceVisibility, KnowledgeSourceStatus
from sentra_core.domain.entities.document_entity import DocumentFileType, DocumentStatus
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


# RAG Query Schemas
class DocumentChunkResponse(BaseModel):
    chunk_id: str = Field(..., description="Unique identifier for the chunk")
    content: str = Field(..., description="Text content of the chunk")
    metadata: Dict[str, Any] = Field(..., description="Chunk metadata including source info")
    relevance_score: float = Field(..., description="Relevance score (0.0 to 1.0)")


class RAGSearchRequest(BaseModel):
    query: str = Field(..., description="Search query", min_length=1)
    knowledge_source_id: Optional[UUID] = Field(None, description="Optional filter by knowledge source")
    limit: int = Field(default=10, description="Maximum number of results", ge=1, le=50)


class RAGSearchResponse(BaseModel):
    query: str = Field(..., description="Original search query")
    chunks: List[DocumentChunkResponse] = Field(..., description="Relevant document chunks")
    total_results: int = Field(..., description="Total number of results found")


class RAGContextRequest(BaseModel):
    query: str = Field(..., description="Query to generate context for", min_length=1)
    knowledge_source_id: Optional[UUID] = Field(None, description="Optional filter by knowledge source")
    max_tokens: int = Field(default=4000, description="Maximum tokens in context", ge=100, le=8000)


class RAGContextResponse(BaseModel):
    query: str = Field(..., description="Original query")
    context: str = Field(..., description="Formatted context for LLM")
    sources_used: int = Field(..., description="Number of document chunks used")
    estimated_tokens: int = Field(..., description="Estimated token count")

    model_config = {
        "from_attributes": True,
        "populate_by_name": True
    }