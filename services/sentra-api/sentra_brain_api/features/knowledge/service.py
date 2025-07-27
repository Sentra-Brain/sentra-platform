# sentra_brain_api/features/knowledge/service.py

import os
from pathlib import Path
from typing import List, Optional
from fastapi import UploadFile, HTTPException

from sentra_shared.domain.entities.knowledge_source_entity import KnowledgeSourceEntity, KnowledgeSourceType, KnowledgeSourceVisibility, KnowledgeSourceStatus
from sentra_shared.domain.entities.document_entity import DocumentEntity, DocumentFileType
from sentra_shared.domain.entities.user_entity import UserEntity
from sentra_shared.domain.services.file_storage import FileStorageService
from sentra_shared.domain.services.indexing_publisher import IndexingJobPublisher
from sentra_brain_api.core.exceptions import SentraHTTPException
from sentra_shared.core.logging import get_logger
from sentra_shared.domain.repositories.knowledge_repository import KnowledgeRepository
from sentra_brain_api.features.knowledge.models import (
    CreateKnowledgeSourceRequest,
    DocumentUploadRequest
)


logger = get_logger(__name__)


class KnowledgeService:
    def __init__(self, repository: KnowledgeRepository, indexing_publisher: IndexingJobPublisher = None):
        self.repository = repository
        self.indexing_publisher = indexing_publisher or IndexingJobPublisher()
        self._file_storage = None

    ALLOWED_FILE_TYPES = {
        ".pdf": DocumentFileType.PDF,
        ".docx": DocumentFileType.DOCX,
        ".txt": DocumentFileType.TXT,
        ".md": DocumentFileType.MD
    }

    def _get_settings(self):
        """Lazy import of settings to avoid circular imports"""
        from sentra_shared.core.settings import settings
        return settings
    
    def _get_file_storage(self) -> FileStorageService:
        """Lazy initialization of file storage service"""
        if self._file_storage is None:
            settings = self._get_settings()
            self._file_storage = FileStorageService(settings.knowledge_mount_path)
        return self._file_storage

    def create_knowledge_source(self, request: CreateKnowledgeSourceRequest, user: UserEntity) -> KnowledgeSourceEntity:
        """Create a new knowledge source"""
        try:
            settings = self._get_settings()
            
            # Validate folder path if type is FOLDER
            if request.type == KnowledgeSourceType.FOLDER:
                if not request.path:
                    raise HTTPException(status_code=400, detail="Path is required for folder-type knowledge sources")
                
                # Ensure path starts with the allowed mount point
                mount_path = Path(settings.knowledge_mount_path)
                requested_path = Path(request.path)
                
                try:
                    # Check if the path is under the allowed mount
                    requested_path.resolve().relative_to(mount_path.resolve())
                except ValueError:
                    raise HTTPException(
                        status_code=400, 
                        detail=f"Folder path must be under {settings.knowledge_mount_path}"
                    )

            knowledge_source = KnowledgeSourceEntity(
                name=request.name,
                type=request.type,
                path=request.path,
                description=request.description,
                created_by=user.id,
                visibility=request.visibility,
                auto_index=request.auto_index
            )

            return self.repository.create_knowledge_source(knowledge_source)
        except HTTPException as he:
            logger.error(f"HTTP error creating knowledge source: {he.detail}")
            raise he
        except Exception as e:
            logger.error(f"Failed to create knowledge source: {e}")
            raise SentraHTTPException(
                status_code=500,
                code="CREATE_KNOWLEDGE_SOURCE_FAILED",
                message="No se pudo crear el origen de conocimiento.",
                details=str(e),
                path="/knowledge-sources",
                suggestion="Revisa los permisos de acceso al sistema de ficheros o la base de datos."
            )

    def upload_document(self, file: UploadFile, request: DocumentUploadRequest, user: UserEntity) -> DocumentEntity:
        """Upload a document and queue it for indexing"""
        try:
            file_extension = Path(file.filename).suffix.lower()
            
            if file_extension not in self.ALLOWED_FILE_TYPES:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Unsupported file type. Allowed types: {list(self.ALLOWED_FILE_TYPES.keys())}"
                )

            upload_sources = self.repository.list_knowledge_sources(created_by=user.id)
            upload_source = next(
                (source for source in upload_sources if source.type == KnowledgeSourceType.UPLOAD), 
                None
            )
            
            if not upload_source:
                upload_source = KnowledgeSourceEntity(
                    name=f"{user.username}'s Uploads",
                    type=KnowledgeSourceType.UPLOAD,
                    description="Documents uploaded by user",
                    created_by=user.id,
                    visibility=KnowledgeSourceVisibility.PRIVATE,
                    auto_index=True
                )
                upload_source = self.repository.create_knowledge_source(upload_source)

            # Use FileStorageService to save with original filename
            file_storage = self._get_file_storage()
            try:
                absolute_path, relative_path = file_storage.save_file(file.file, file.filename, user.id)
                logger.info(f"File saved: {absolute_path} (relative: {relative_path})")
            except Exception as e:
                logger.error(f"Failed to save file {file.filename}: {e}")
                raise HTTPException(status_code=500, detail="Failed to save file")

            # Create document record using original filename
            document = DocumentEntity(
                filename=file.filename,  # Store original filename
                display_name=request.display_name,
                description=request.description,
                filetype=self.ALLOWED_FILE_TYPES[file_extension],
                path=relative_path,  # Store relative path for consistency
                uploaded_by=user.id,
                knowledge_source_id=upload_source.id
            )

            document = self.repository.create_document(document)

            # Queue for indexing using new publisher
            try:
                with self.indexing_publisher:
                    success = self.indexing_publisher.publish_indexing_job(
                        document_id=str(document.id),
                        document_path=relative_path,  # Use relative path
                        knowledge_source_id=str(upload_source.id),
                        filename=file.filename,
                        uploaded_by=str(user.id)
                    )
                    if success:
                        logger.info(f"Document {document.id} queued for indexing")
                    else:
                        logger.warning(f"Failed to queue document {document.id} for indexing")
            except Exception as e:
                logger.error(f"Failed to queue document {document.id} for indexing: {e}")
                # Continue - document is saved but indexing will need to be retried

            return document
        except HTTPException as he:
            logger.error(f"HTTP error uploading document: {he.detail}")
            raise he
        except Exception as e:
            logger.error(f"Failed to upload document: {e}")
            raise SentraHTTPException(
                status_code=500,
                code="UPLOAD_DOCUMENT_FAILED",
                message="No se pudo subir el documento.",
                details=str(e),
                path="/knowledge/upload",
                suggestion="Revisa los permisos de acceso al sistema de ficheros o la base de datos."
            )

    def list_knowledge_sources(self, user: UserEntity, limit: int = 100, offset: int = 0) -> tuple[List[KnowledgeSourceEntity], int]:
        """List knowledge sources for a user"""
        try:
            sources = self.repository.list_knowledge_sources(created_by=user.id, limit=limit, offset=offset)
            total = self.repository.get_knowledge_sources_count(created_by=user.id)
            return sources, total
        except Exception as e:
            logger.error(f"Failed to list knowledge sources: {e}")
            raise SentraHTTPException(
                status_code=500,
                code="LIST_KNOWLEDGE_SOURCES_FAILED",
                message="No se pudo listar las fuentes de conocimiento.",
                details=str(e),
                path="/knowledge/sources",
                suggestion="Revisa los permisos de acceso a la base de datos."
            )

    def list_documents(self, user: UserEntity, knowledge_source_id: Optional[str] = None, 
                      limit: int = 100, offset: int = 0) -> tuple[List[DocumentEntity], int]:
        """List documents for a user"""
        try:            
            from uuid import UUID
            source_uuid = UUID(knowledge_source_id) if knowledge_source_id else None
            documents = self.repository.list_documents(
                uploaded_by=user.id, 
                knowledge_source_id=source_uuid, 
                limit=limit, 
                offset=offset
            )
            total = self.repository.get_documents_count(
                uploaded_by=user.id, 
                knowledge_source_id=source_uuid
            )
            return documents, total
        except Exception as e:
            logger.error(f"Failed to list documents: {e}")
            raise SentraHTTPException(
                status_code=500,
                code="LIST_DOCUMENTS_FAILED",
                message="No se pudo listar los documentos.",
                details=str(e),
                path="/knowledge/documents",
                suggestion="Revisa los permisos de acceso a la base de datos."
            )
