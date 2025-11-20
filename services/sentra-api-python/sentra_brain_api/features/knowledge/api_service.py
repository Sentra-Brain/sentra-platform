# sentra_brain_api/features/knowledge/api_service.py

from pathlib import Path
from uuid import UUID
from typing import List, Optional
from fastapi import UploadFile
 
from sentra.domain.constants.file_types import ALLOWED_FILE_TYPES
from sentra.domain.entities.knowledge_source_entity import KnowledgeSourceEntity
from sentra.domain.entities.document_entity import DocumentEntity
from sentra.domain.entities.user_entity import UserEntity
from sentra.infra.amqp.indexing_publisher import IndexingJobPublisher
from sentra.infra.storage.file_storage import FileStorageService
from sentra.domain.services.knowledge_source_service import KnowledgeSourceService
from sentra.domain.services.document_service import DocumentService
from sentra.infra.sql.repositories.knowledge_source_repository_sql import KnowledgeSourceRepositorySql
from sentra.infra.sql.repositories.document_repository_sql import DocumentRepositorySql
from sentra.domain.enums.knowledge import KnowledgeSourceType, KnowledgeSourceVisibility
from sentra_brain_api.core.exceptions import SentraHTTPException
from sentra_brain_api.features.knowledge.schemas import CreateKnowledgeSourceRequest, DocumentMarkdownResponse, DocumentUploadRequest
from sentra.shared.settings import settings
from sentra.shared.logging import get_logger

logger = get_logger(__name__)


class KnowledgeApiService:
    def __init__(
        self,
        knowledge_repo: KnowledgeSourceRepositorySql,
        document_repo: DocumentRepositorySql,
        indexing_publisher: IndexingJobPublisher
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
            raise SentraHTTPException(
                status_code=400, code="INVALID_KNOWLEDGE_SOURCE", message=str(ve), suggestion="Revisa el path indicado")
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
            filetype=ALLOWED_FILE_TYPES[ext],
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

    def list_documents(self, user: UserEntity, source_id: Optional[UUID], limit: int, offset: int) -> tuple[List[DocumentEntity], int]:
        return (
            self.document_repo.list_by_user_or_source(user.id, source_id, limit, offset),
            self.document_repo.count_by_user_or_source(user.id, source_id)
        )

    def update_knowledge_source_status(self, source_id: UUID, enabled: bool) -> KnowledgeSourceEntity:
        return self.knowledge_svc.update_status(source_id, enabled)

    def reindex_document(self, document_id: UUID, user: UserEntity) -> DocumentEntity:
        doc = self.document_svc.mark_for_reindex(document_id, user.id)
        try:
            with self.indexing_publisher:
                self.indexing_publisher.publish_indexing_job(
                    document_id=doc.id,
                    document_path=doc.path,
                    knowledge_source_id=doc.knowledge_source_id,
                    filename=doc.filename,
                    uploaded_by=user.id
                )
        except Exception as e:
            logger.warning(f"Indexing failed for document {doc.id}: {e}")
        return doc

    def remove_document(self, document_id: UUID, user: UserEntity) -> DocumentEntity:
        return self.document_svc.mark_for_removal(document_id, user.id)

    def get_knowledge_source(self, source_id: UUID, user: UserEntity) -> KnowledgeSourceEntity:
        """Get a single knowledge source by ID"""
        source = self.knowledge_repo.get(source_id)
        if not source:
            raise SentraHTTPException(
                status_code=404,
                code="KNOWLEDGE_SOURCE_NOT_FOUND",
                message=f"Knowledge source with ID {source_id} not found",
                path=f"/knowledge/sources/{source_id}"
            )
        return source

    def delete_knowledge_source(self, source_id: UUID, user: UserEntity) -> KnowledgeSourceEntity:
        """Delete a knowledge source (admin only)"""
        try:
            return self.knowledge_svc.delete_knowledge_source(source_id)
        except Exception as e:
            raise SentraHTTPException(
                status_code=500,
                code="DELETE_KNOWLEDGE_SOURCE_FAILED",
                message="Could not delete knowledge source",
                details=str(e),
                path=f"/knowledge/sources/{source_id}",
                suggestion="Check if source has documents or database constraints."
            )

    def upload_document_to_source(self, knowledge_source_id: UUID, file: UploadFile, request: DocumentUploadRequest, user: UserEntity) -> DocumentEntity:
        """Upload a document to a specific knowledge source"""
        ext = Path(file.filename).suffix.lower()
        if ext not in ALLOWED_FILE_TYPES:
            raise SentraHTTPException(
                status_code=400,
                code="INVALID_FILE_TYPE",
                message=f"File type '{ext}' is not allowed. Allowed types: {', '.join(ALLOWED_FILE_TYPES)}",
                path=f"/knowledge/sources/{knowledge_source_id}/documents"
            )

        # Get the specified knowledge source
        source = self.knowledge_repo.get(knowledge_source_id)
        if not source:
            raise SentraHTTPException(
                status_code=404,
                code="KNOWLEDGE_SOURCE_NOT_FOUND",
                message=f"Knowledge source with ID {knowledge_source_id} not found",
                path=f"/knowledge/sources/{knowledge_source_id}/documents"
            )

        try:
            abs_path, rel_path = self._file_storage.save_file(file.file, file.filename, user.id)
        except Exception as e:
            raise SentraHTTPException(
                status_code=500,
                code="FILE_STORAGE_ERROR",
                message="Could not save file to storage.",
                details=str(e),
                path=f"/knowledge/sources/{knowledge_source_id}/documents",
                suggestion="Check file system permissions."
            )

        document = DocumentEntity(
            filename=file.filename,
            display_name=request.display_name,
            description=request.description,
            filetype=ALLOWED_FILE_TYPES[ext],
            path=rel_path,
            created_by_id=user.id,
            knowledge_source_id=source.id
        )
        document = self.document_repo.create(document)

        try:
            with self.indexing_publisher:
                self.indexing_publisher.publish_indexing_job(
                    document_id=document.id,
                    document_path=rel_path,
                    knowledge_source_id=source.id,
                    filename=file.filename,
                    uploaded_by=user.id
                )
        except Exception as e:
            logger.warning(f"Indexing failed for document {document.id}: {e}")

        return document

    def get_document(self, document_id: UUID, user: UserEntity) -> DocumentEntity:
        """Get a single document by ID"""
        doc = self.document_repo.get(document_id)
        if not doc:
            raise SentraHTTPException(
                status_code=404,
                code="DOCUMENT_NOT_FOUND",
                message=f"Document with ID {document_id} not found",
                path=f"/knowledge/documents/{document_id}"
            )
        return doc

    def update_document(self, document_id: UUID, display_name: Optional[str], description: Optional[str], user: UserEntity) -> DocumentEntity:
        """Update document metadata"""
        doc = self.document_repo.get(document_id)
        if not doc:
            raise SentraHTTPException(
                status_code=404,
                code="DOCUMENT_NOT_FOUND",
                message=f"Document with ID {document_id} not found",
                path=f"/knowledge/documents/{document_id}"
            )
        
        if display_name is not None:
            doc.display_name = display_name
        if description is not None:
            doc.description = description
            
        return self.document_repo.update(doc)

    def get_document_markdown(self, document_id: UUID, user: UserEntity) -> DocumentMarkdownResponse:
        """Get markdown info for a document"""
        doc = self.get_document(document_id, user)
        if not doc.has_markdown or not doc.markdown_path:
            raise SentraHTTPException(
                status_code=404,
                code="DOCUMENT_MARKDOWN_NOT_FOUND",
                message=f"Document with ID {document_id} does not have markdown info",
                path=f"/knowledge/documents/{document_id}/markdown"
            )
        # Get markdown content
        content_bytes = self._file_storage.get_file_content(doc.markdown_path)
        if content_bytes is None:
            raise SentraHTTPException(
                status_code=404,
                code="DOCUMENT_MARKDOWN_NOT_FOUND",
                message=f"Markdown content for document {document_id} not found",
                path=f"/knowledge/documents/{document_id}/markdown"
            )
        # convert bytes to string
        markdown = content_bytes.decode("utf-8")
        return DocumentMarkdownResponse(document_id=document_id, markdown=markdown)
