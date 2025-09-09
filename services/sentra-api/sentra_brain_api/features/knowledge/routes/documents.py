# sentra_brain_api/features/knowledge/routes/documents.py

from fastapi import APIRouter, Depends, UploadFile, File, Form, Query, HTTPException
from uuid import UUID
from sqlalchemy.orm import Session
from typing import Optional

from sentra.infra.sql.postgres_service import get_db
from sentra.domain.entities.user_entity import UserEntity
from sentra.infra.sql.repositories.knowledge_source_repository_sql import KnowledgeSourceRepositorySql
from sentra.infra.sql.repositories.document_repository_sql import DocumentRepositorySql
from sentra.infra.amqp.indexing_publisher import IndexingJobPublisher

from sentra_brain_api.features.knowledge.api_service import KnowledgeApiService
from sentra_brain_api.features.knowledge.schemas import (
    DocumentMarkdownResponse,
    DocumentUploadRequest,
    DocumentResponse, 
    DocumentListResponse
)
from sentra_brain_api.features.knowledge.mappers import to_document_response
from sentra_brain_api.crosscutting.authorization import get_authenticated_user

router = APIRouter()

def _get_service(db: Session = Depends(get_db)) -> KnowledgeApiService:
    return KnowledgeApiService(
        knowledge_repo=KnowledgeSourceRepositorySql(db),
        document_repo=DocumentRepositorySql(db),
        indexing_publisher=IndexingJobPublisher()
    )

# Routes for /knowledge/sources/{id}/documents
@router.get("/sources/{knowledge_source_id}/documents", response_model=DocumentListResponse)
async def list_documents_in_source(
    knowledge_source_id: UUID,
    user: UserEntity = Depends(get_authenticated_user),
    service: KnowledgeApiService = Depends(_get_service)
):
    """List all documents in a specific knowledge source"""
    docs, total = service.list_documents(user, knowledge_source_id, limit=1000, offset=0)
    return DocumentListResponse(
        documents=[DocumentResponse.model_validate(doc) for doc in docs],
        total=total
    )

@router.post("/sources/{knowledge_source_id}/documents", response_model=DocumentResponse)
async def upload_document_to_source(
    knowledge_source_id: UUID,
    file: UploadFile = File(...),
    display_name: str = Form(...),
    description: Optional[str] = Form(None),
    user: UserEntity = Depends(get_authenticated_user),
    service: KnowledgeApiService = Depends(_get_service)
):
    """Upload a document to a specific knowledge source"""
    # This will need to be updated in the service to accept knowledge_source_id
    doc = service.upload_document_to_source(
        knowledge_source_id,
        file, 
        DocumentUploadRequest(display_name=display_name, description=description), 
        user
    )
    return to_document_response(doc)

# Routes for /knowledge/documents (root level document operations)
@router.get("/documents", response_model=DocumentListResponse)
async def list_all_documents(
    knowledge_source_id: Optional[UUID] = Query(None),
    limit: int = Query(100), 
    offset: int = Query(0),
    user: UserEntity = Depends(get_authenticated_user),
    service: KnowledgeApiService = Depends(_get_service)
):
    """List all documents, optionally filtered by knowledge source"""
    docs, total = service.list_documents(user, knowledge_source_id, limit, offset)
    return DocumentListResponse(
        documents=[to_document_response(d) for d in docs],
        total=total
    )

@router.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: UUID,
    user: UserEntity = Depends(get_authenticated_user),
    service: KnowledgeApiService = Depends(_get_service)
):
    """Get a specific document by ID"""
    # This will need to be implemented in the service
    doc = service.get_document(document_id, user)
    return to_document_response(doc)

@router.patch("/documents/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: UUID,
    display_name: Optional[str] = None,
    description: Optional[str] = None,
    user: UserEntity = Depends(get_authenticated_user),
    service: KnowledgeApiService = Depends(_get_service)
):
    """Update document metadata (name, description)"""
    # This will need to be implemented in the service
    doc = service.update_document(document_id, display_name, description, user)
    return to_document_response(doc)

@router.post("/documents/{document_id}/reindex", response_model=DocumentResponse)
async def reindex_document(
    document_id: UUID,
    user: UserEntity = Depends(get_authenticated_user),
    service: KnowledgeApiService = Depends(_get_service)
):
    doc = service.reindex_document(document_id, user)
    return to_document_response(doc)

@router.delete("/documents/{document_id}", response_model=DocumentResponse)
async def remove_document(
    document_id: UUID,
    user: UserEntity = Depends(get_authenticated_user),
    service: KnowledgeApiService = Depends(_get_service)
):
    """Remove a document"""
    doc = service.remove_document(document_id, user)
    return to_document_response(doc)

@router.get("/documents/{document_id}/markdown", response_model=DocumentMarkdownResponse)
async def get_document_markdown(
    document_id: UUID,
    user: UserEntity = Depends(get_authenticated_user),
    service: KnowledgeApiService = Depends(_get_service)
):
    """Get the markdown content of a specific document"""
    markdown_response = service.get_document_markdown(document_id, user)
    return markdown_response