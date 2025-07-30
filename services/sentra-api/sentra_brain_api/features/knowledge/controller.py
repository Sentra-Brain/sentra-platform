from fastapi import APIRouter, Depends, UploadFile, File, Form, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from sentra_shared.infra.sql.postgres_service import get_db
from sentra_shared.domain.entities.user_entity import UserEntity
from sentra_shared.domain.enums.role import Role
from sentra_shared.domain.repository.knowledge_source_repository import KnowledgeSourceRepository
from sentra_shared.domain.repository.document_repository import DocumentRepository
from sentra_shared.domain.services.indexing_publisher import IndexingJobPublisher

from sentra_brain_api.features.knowledge.api_service import KnowledgeApiService
from sentra_brain_api.features.knowledge.schemas import (
    CreateKnowledgeSourceRequest, DocumentUploadRequest,
    KnowledgeSourceResponse, KnowledgeSourceListResponse,
    DocumentResponse, DocumentListResponse
)
from sentra_brain_api.features.knowledge.mappers import (
    to_document_response, to_knowledge_source_response
)
from sentra_brain_api.crosscutting.authorization import get_authenticated_user


class KnowledgeController:
    def __init__(self):
        self.router = APIRouter()
        self._add_routes()

    def _get_service(self, db: Session = Depends(get_db)) -> KnowledgeApiService:
        return KnowledgeApiService(
            knowledge_repo=KnowledgeSourceRepository(db),
            document_repo=DocumentRepository(db),
            indexing_publisher=IndexingJobPublisher()
        )

    def _require_admin(self, user: UserEntity = Depends(get_authenticated_user)) -> UserEntity:
        if Role.ADMIN.value not in user.roles.split(","):
            raise HTTPException(status_code=403, detail="Admin role required")
        return user


    def _add_routes(self):
    
        @self.router.post("/knowledge-sources", response_model=KnowledgeSourceResponse)
        async def create_knowledge_source(
            request: CreateKnowledgeSourceRequest,
            user: UserEntity = Depends(self._require_admin),
            service: KnowledgeApiService = Depends(self._get_service)
        ):
            """Create a new knowledge source (admin only)"""
            knowledge_source = service.create_knowledge_source(request, user)
            return KnowledgeSourceResponse.model_validate(knowledge_source)
    
        @self.router.post("/upload", response_model=DocumentResponse)
        async def upload_document(
            file: UploadFile = File(...),
            display_name: str = Form(...),
            description: Optional[str] = Form(None),
            user: UserEntity = Depends(get_authenticated_user),
            service: KnowledgeApiService = Depends(self._get_service)
        ):
            doc = service.upload_document(file, DocumentUploadRequest(display_name=display_name, description=description), user)
            return to_document_response(doc)

        @self.router.get("/knowledge-sources", response_model=KnowledgeSourceListResponse)
        async def list_knowledge_sources(
            limit: int = Query(100), offset: int = Query(0),
            user: UserEntity = Depends(get_authenticated_user),
            service: KnowledgeApiService = Depends(self._get_service)
        ):
            sources, total = service.list_knowledge_sources(user, limit, offset)
            return KnowledgeSourceListResponse(
                sources=[to_knowledge_source_response(src) for src in sources],
                total=total
            )

        @self.router.get("/knowledge-sources/{knowledge_source_id}/documents")
        async def list_documents(
            knowledge_source_id: str,
            user: UserEntity = Depends(get_authenticated_user),
            service: KnowledgeApiService = Depends(self._get_service)
        ):
            docs, total = service.list_documents(user, knowledge_source_id, limit=1000, offset=0)
            return DocumentListResponse(
                documents=[DocumentResponse.model_validate(doc) for doc in docs],
                total=total
            )

        @self.router.put("/knowledge-sources/{knowledge_source_id}/status", response_model=KnowledgeSourceResponse)
        async def update_status(
            knowledge_source_id: str,
            enabled: bool,
            user: UserEntity = Depends(self._require_admin),
            service: KnowledgeApiService = Depends(self._get_service)
        ):
            updated = service.update_knowledge_source_status(knowledge_source_id, enabled)
            return to_knowledge_source_response(updated)

        @self.router.get("/documents", response_model=DocumentListResponse)
        async def list_documents(
            knowledge_source_id: Optional[str] = Query(None),
            limit: int = Query(100), offset: int = Query(0),
            user: UserEntity = Depends(get_authenticated_user),
            service: KnowledgeApiService = Depends(self._get_service)
        ):
            docs, total = service.list_documents(user, knowledge_source_id, limit, offset)
            return DocumentListResponse(
                documents=[to_document_response(d) for d in docs],
                total=total
            )



        @self.router.delete("/documents/{document_id}", response_model=DocumentResponse)
        async def remove_document(
            document_id: str,
            user: UserEntity = Depends(get_authenticated_user),
            service: KnowledgeApiService = Depends(self._get_service)
        ):
            doc = service.remove_document(document_id, user)
            return to_document_response(doc)
