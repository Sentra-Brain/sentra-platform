# sentra_brain_api/features/knowledge/controller.py

from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Query
from sqlalchemy.orm import Session

from sentra_brain_api.crosscutting.authorization import get_authenticated_user
from sentra_brain_api.domain.user_entity import UserEntity
from sentra_brain_api.domain.role import Role
from sentra_brain_api.infra.postgres_service import get_db
from sentra_brain_api.infra.rabbitmq.publisher import get_rabbitmq_publisher
from sentra_brain_api.features.knowledge.repository import KnowledgeRepository
from sentra_brain_api.features.knowledge.service import KnowledgeService
from sentra_brain_api.features.knowledge.schemas import (
    CreateKnowledgeSourceRequest,
    DocumentUploadRequest,
    KnowledgeSourceResponse,
    KnowledgeSourceListResponse,
    DocumentResponse,
    DocumentListResponse
)
from sentra_brain_api.crosscutting.logging import get_logger

logger = get_logger(__name__)


class KnowledgeController:
    def __init__(self):
        self.router = APIRouter()
        self._add_routes()

    def _get_service(self, db: Session = Depends(get_db)) -> KnowledgeService:
        repository = KnowledgeRepository(db)
        publisher = get_rabbitmq_publisher()
        return KnowledgeService(repository, publisher)

    def _require_admin(self, user: UserEntity = Depends(get_authenticated_user)) -> UserEntity:
        """Dependency to require admin role"""
        if Role.ADMIN.value not in set(user.roles.split(",")):
            raise HTTPException(status_code=403, detail="Admin role required")
        return user

    def _add_routes(self):
        @self.router.post("/upload", response_model=DocumentResponse)
        async def upload_document(
            file: UploadFile = File(...),
            display_name: str = Form(...),
            description: Optional[str] = Form(None),
            user: UserEntity = Depends(get_authenticated_user),
            service: KnowledgeService = Depends(self._get_service)
        ):
            """Upload a document for indexing"""
            request = DocumentUploadRequest(
                display_name=display_name,
                description=description
            )
            document = service.upload_document(file, request, user)
            return DocumentResponse.model_validate(document)

        @self.router.post("/knowledge-sources", response_model=KnowledgeSourceResponse)
        async def create_knowledge_source(
            request: CreateKnowledgeSourceRequest,
            user: UserEntity = Depends(self._require_admin),
            service: KnowledgeService = Depends(self._get_service)
        ):
            """Create a new knowledge source (admin only)"""
            knowledge_source = service.create_knowledge_source(request, user)
            return KnowledgeSourceResponse.model_validate(knowledge_source)

        @self.router.get("/knowledge-sources", response_model=KnowledgeSourceListResponse)
        async def list_knowledge_sources(
            limit: int = Query(default=100, le=1000),
            offset: int = Query(default=0, ge=0),
            user: UserEntity = Depends(get_authenticated_user),
            service: KnowledgeService = Depends(self._get_service)
        ):
            """List knowledge sources for the current user"""
            sources, total = service.list_knowledge_sources(user, limit, offset)
            return KnowledgeSourceListResponse(
                sources=[KnowledgeSourceResponse.model_validate(source) for source in sources],
                total=total
            )

        @self.router.get("/documents", response_model=DocumentListResponse)
        async def list_documents(
            knowledge_source_id: Optional[str] = Query(None),
            limit: int = Query(default=100, le=1000),
            offset: int = Query(default=0, ge=0),
            user: UserEntity = Depends(get_authenticated_user),
            service: KnowledgeService = Depends(self._get_service)
        ):
            """List documents for the current user"""
            documents, total = service.list_documents(user, knowledge_source_id, limit, offset)
            return DocumentListResponse(
                documents=[DocumentResponse.model_validate(doc) for doc in documents],
                total=total
            )