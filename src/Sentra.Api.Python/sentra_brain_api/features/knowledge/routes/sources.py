# sentra_brain_api/features/knowledge/routes/sources.py

from fastapi import APIRouter, Depends, Query, HTTPException
from uuid import UUID
from sqlalchemy.orm import Session
from typing import Optional

from sentra.infra.sql.postgres_service import get_db
from sentra.domain.entities.user_entity import UserEntity
from sentra.domain.enums.role import Role
from sentra.infra.sql.repositories.knowledge_source_repository_sql import KnowledgeSourceRepositorySql
from sentra.infra.sql.repositories.document_repository_sql import DocumentRepositorySql
from sentra.infra.amqp.indexing_publisher import IndexingJobPublisher

from sentra_brain_api.features.knowledge.api_service import KnowledgeApiService
from sentra_brain_api.features.knowledge.schemas import (
    CreateKnowledgeSourceRequest,
    KnowledgeSourceResponse, 
    KnowledgeSourceListResponse
)
from sentra_brain_api.features.knowledge.mappers import to_knowledge_source_response
from sentra_brain_api.crosscutting.authorization import get_authenticated_user

router = APIRouter()

def _get_service(db: Session = Depends(get_db)) -> KnowledgeApiService:
    return KnowledgeApiService(
        knowledge_repo=KnowledgeSourceRepositorySql(db),
        document_repo=DocumentRepositorySql(db),
        indexing_publisher=IndexingJobPublisher()
    )

def _require_admin(user: UserEntity = Depends(get_authenticated_user)) -> UserEntity:
    if Role.ADMIN.value not in user.roles.split(","):
        raise HTTPException(status_code=403, detail="Admin role required")
    return user

@router.get("", response_model=KnowledgeSourceListResponse)
async def list_knowledge_sources(
    limit: int = Query(100), 
    offset: int = Query(0),
    user: UserEntity = Depends(get_authenticated_user),
    service: KnowledgeApiService = Depends(_get_service)
):
    """List all knowledge sources"""
    sources, total = service.list_knowledge_sources(user, limit, offset)
    return KnowledgeSourceListResponse(
        sources=[to_knowledge_source_response(src) for src in sources],
        total=total
    )

@router.post("", response_model=KnowledgeSourceResponse)
async def create_knowledge_source(
    request: CreateKnowledgeSourceRequest,
    user: UserEntity = Depends(_require_admin),
    service: KnowledgeApiService = Depends(_get_service)
):
    """Create a new knowledge source (admin only)"""
    knowledge_source = service.create_knowledge_source(request, user)
    return KnowledgeSourceResponse.model_validate(knowledge_source)

@router.get("/{knowledge_source_id}", response_model=KnowledgeSourceResponse)
async def get_knowledge_source(
    knowledge_source_id: UUID,
    user: UserEntity = Depends(get_authenticated_user),
    service: KnowledgeApiService = Depends(_get_service)
):
    """Get a single knowledge source by ID"""
    # This will need to be implemented in the service
    knowledge_source = service.get_knowledge_source(knowledge_source_id, user)
    return to_knowledge_source_response(knowledge_source)

@router.patch("/{knowledge_source_id}", response_model=KnowledgeSourceResponse)
async def update_knowledge_source(
    knowledge_source_id: UUID,
    enabled: Optional[bool] = None,
    user: UserEntity = Depends(_require_admin),
    service: KnowledgeApiService = Depends(_get_service)
):
    """Update knowledge source metadata or status (admin only)"""
    if enabled is not None:
        # Handle status update (previously /knowledge-sources/{id}/status)
        updated = service.update_knowledge_source_status(knowledge_source_id, enabled)
        return to_knowledge_source_response(updated)
    else:
        # For future: handle other metadata updates
        raise HTTPException(status_code=400, detail="No update parameters provided")

@router.delete("/{knowledge_source_id}", response_model=KnowledgeSourceResponse)
async def delete_knowledge_source(
    knowledge_source_id: UUID,
    user: UserEntity = Depends(_require_admin),
    service: KnowledgeApiService = Depends(_get_service)
):
    """Delete a knowledge source (admin only)"""
    # This will need to be implemented in the service
    deleted_source = service.delete_knowledge_source(knowledge_source_id, user)
    return to_knowledge_source_response(deleted_source)