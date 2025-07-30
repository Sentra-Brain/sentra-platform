# sentra_brain_api/features/knowledge/api_service.py

from pathlib import Path
from uuid import UUID
from typing import List, Optional
from fastapi import UploadFile

from sentra_shared.domain.constants.file_types import ALLOWED_FILE_TYPES
from sentra_shared.domain.entities.knowledge_source_entity import KnowledgeSourceEntity
from sentra_shared.domain.entities.document_entity import DocumentEntity
from sentra_shared.domain.entities.user_entity import UserEntity
from sentra_shared.domain.services.indexing_publisher import IndexingJobPublisher
from sentra_shared.domain.services.file_storage import FileStorageService
from sentra_shared.domain.services.knowledge_source_service import KnowledgeSourceService
from sentra_shared.domain.services.document_service import DocumentService
from sentra_shared.domain.repository.knowledge_source_repository import KnowledgeSourceRepository
from sentra_shared.domain.repository.document_repository import DocumentRepository
from sentra_shared.domain.enums.knowledge import KnowledgeSourceType, KnowledgeSourceVisibility
from sentra_shared.domain.enums.document import DocumentFileType
from sentra_brain_api.core.exceptions import SentraHTTPException
from sentra_brain_api.features.knowledge.schemas import CreateKnowledgeSourceRequest, DocumentUploadRequest
from sentra_shared.core.settings import settings
from sentra_shared.core.logging import get_logger

logger = get_logger(__name__)


class KnowledgeApiService:
    def __init__(
        self,
        knowledge_repo: KnowledgeSourceRepository,
        document_repo: DocumentRepository,
        indexing_publisher: IndexingJobPublisher = None
    ):
        self.knowledge_repo = knowledge_repo
        self.document_repo = document_repo
        self.indexing_publisher = indexing_publisher or IndexingJobPublisher()
        self.knowledge_svc = KnowledgeSourceService(knowledge_repo, mount_path=settings.knowledge_mount_path)
        self.document_svc = DocumentService(document_repo)
        self._file_storage = FileStorageService(settings.knowledge_mount_path)

    def create_knowledge_source(self, request: CreateKnowledgeSourceRequest, user: UserEntity) -> KnowledgeSourceEntity:
        entity = KnowledgeSourceEntity(
            name=request.name,
            type=request.type,
            path=request.path,
            description=request.description,
            created_by_id=user.id,
            visibility=request.visibility,
            auto_index=request.auto_index
        )
        try:
            return self.knowledge_svc.create_knowledge_source(entity)
        except ValueError as ve:
            raise SentraHTTPException(400, "INVALID_KNOWLEDGE_SOURCE", str(ve), suggestion="Revisa el path indicado")
        except Exception as e:
            raise SentraHTTPException(
                status_code=500,
                code="CREATE_KNOWLEDGE_SOURCE_FAILED",
                message="Could not create knowledge source",
                details=str(e),
                path="/knowledge-sources",
                suggestion="Check file system or database access permissions."
            )

    def upload_document(self, file: UploadFile, request: DocumentUploadRequest, user: UserEntity) -> DocumentEntity:
        ext = Path(file.filename).suffix.lower()
        if ext not in ALLOWED_FILE_TYPES:
            raise SentraHTTPException(
                status_code=400,
                code="INVALID_FILE_TYPE",
                message=f"File type '{ext}' is not allowed. Allowed types: {', '.join(ALLOWED_FILE_TYPES)}",
                path="/upload"
            )

        upload_source = next(
            (src for src in self.knowledge_repo.list_by_user(user.id) if src.type == KnowledgeSourceType.UPLOAD),
            None
        )

        if not upload_source:
            upload_source = KnowledgeSourceEntity(
                name=f"{user.username}'s Uploads",
                type=KnowledgeSourceType.UPLOAD,
                created_by_id=user.id,
                auto_index=True,
                visibility=KnowledgeSourceVisibility.PRIVATE
            )
            upload_source = self.knowledge_repo.create(upload_source)

        try:
            abs_path, rel_path = self._file_storage.save_file(file.file, file.filename, user.id)
        except Exception as e:
            raise SentraHTTPException(
                status_code=500,
                code="FILE_STORAGE_ERROR",
                message="Could not save file to storage.",
                details=str(e),
                path="/upload",
                suggestion="Check file system permissions."
            )

        document = DocumentEntity(
            filename=file.filename,
            display_name=request.display_name,
            description=request.description,
            filetype=self.ALLOWED_FILE_TYPES[ext],
            path=rel_path,
            created_by_id=user.id,
            knowledge_source_id=upload_source.id
        )
        document = self.document_repo.create(document)

        try:
            with self.indexing_publisher:
                self.indexing_publisher.publish_indexing_job(
                    document_id=str(document.id),
                    document_path=rel_path,
                    knowledge_source_id=str(upload_source.id),
                    filename=file.filename,
                    uploaded_by=str(user.id)
                )
        except Exception as e:
            logger.warning(f"Indexing failed for document {document.id}: {e}")

        return document

    def list_knowledge_sources(self, user: UserEntity, limit: int, offset: int) -> tuple[List[KnowledgeSourceEntity], int]:
        return self.knowledge_repo.list_by_user(user.id, limit, offset), self.knowledge_repo.count_by_user(user.id)

    def list_documents(self, user: UserEntity, source_id: Optional[str], limit: int, offset: int) -> tuple[List[DocumentEntity], int]:
        source_uuid = UUID(source_id) if source_id else None
        return (
            self.document_repo.list_by_user_or_source(user.id, source_uuid, limit, offset),
            self.document_repo.count_by_user_or_source(user.id, source_uuid)
        )

    def update_knowledge_source_status(self, source_id: str, enabled: bool) -> KnowledgeSourceEntity:
        return self.knowledge_svc.update_status(UUID(source_id), enabled)

    def reindex_document(self, document_id: str, user: UserEntity) -> DocumentEntity:
        doc = self.document_svc.mark_for_reindex(UUID(document_id), user.id)
        try:
            with self.indexing_publisher:
                self.indexing_publisher.publish_indexing_job(
                    document_id=str(doc.id),
                    document_path=doc.path,
                    knowledge_source_id=str(doc.knowledge_source_id),
                    filename=doc.filename,
                    uploaded_by=str(user.id)
                )
        except Exception as e:
            logger.warning(f"Indexing failed for document {doc.id}: {e}")
        return doc

    def remove_document(self, document_id: str, user: UserEntity) -> DocumentEntity:
        return self.document_svc.mark_for_removal(UUID(document_id), user.id)
