# sentra_brain_api/features/knowledge/service.py

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
from sentra_shared.domain.repository.knowledge_source_repository import KnowledgeRepository
from sentra_brain_api.features.knowledge.models import (
    CreateKnowledgeSourceRequest,
    DocumentUploadRequest
)

from sentra_brain_api.features.knowledge.models import KnowledgeSourceResponse, DocumentResponse

from sentra_brain_api.shared_models.user_refs import UserRef


logger = get_logger(__name__)


class KnowledgeService:
    def get_documents_by_knowledge_source(self, knowledge_source_id: str, user: UserEntity, limit: int = 100, offset: int = 0) -> tuple[List[dict], int]:
        """Get documents for a specific knowledge source, using navigation property for uploader's name"""
        from uuid import UUID
        source_uuid = UUID(knowledge_source_id)
        documents = self.repository.list_documents(
            knowledge_source_id=source_uuid,
            limit=limit,
            offset=offset
        )
        total = self.repository.get_documents_count(
            knowledge_source_id=source_uuid
        )
        result = []
        for doc in documents:
            user = doc.created_by
            user_ref = UserRef(id=user.id, full_name=user.full_name) if user else None

            result.append(
                DocumentResponse(
                    id=doc.id,
                    filename=doc.filename,
                    display_name=doc.display_name,
                    description=doc.description,
                    filetype=doc.filetype,
                    path=doc.path,
                    created_by=user_ref,
                    created_at=doc.created_at,
                    status=doc.status,
                    status_message=doc.status_message,
                    error=doc.error,
                    chunks_count=doc.chunks_count,
                    knowledge_source_id=doc.knowledge_source_id
                )
            )
        return result, total
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

    def update_knowledge_source_status(self, knowledge_source_id: str, enabled: bool, user: UserEntity) -> KnowledgeSourceEntity:
        """Enable or disable a knowledge source"""
        try:
            from uuid import UUID
            source_uuid = UUID(knowledge_source_id)
            
            # Get the knowledge source
            knowledge_source = self.repository.get_knowledge_source_by_id(source_uuid)
            if not knowledge_source:
                raise HTTPException(status_code=404, detail="Knowledge source not found")
            
            # Update status
            from sentra_shared.domain.entities.knowledge_source_entity import KnowledgeSourceStatus
            new_status = KnowledgeSourceStatus.ACTIVE if enabled else KnowledgeSourceStatus.DISABLED
            knowledge_source.status = new_status
            
            # Save to database
            updated_source = self.repository.update_knowledge_source(knowledge_source)
            logger.info(f"Knowledge source {knowledge_source_id} status changed to {new_status.value} by {user.id}")
            
            return updated_source
        except HTTPException as he:
            logger.error(f"HTTP error updating knowledge source status: {he.detail}")
            raise he
        except Exception as e:
            logger.error(f"Failed to update knowledge source status: {e}")
            raise SentraHTTPException(
                status_code=500,
                code="UPDATE_KNOWLEDGE_SOURCE_STATUS_FAILED", 
                message="No se pudo actualizar el estado de la fuente de conocimiento.",
                details=str(e),
                path="/knowledge/knowledge-sources/status",
                suggestion="Revisa los permisos de acceso a la base de datos."
            )

    def reindex_document(self, document_id: str, user: UserEntity) -> DocumentEntity:
        """Re-index a document by queuing it for indexing"""
        try:
            from uuid import UUID
            doc_uuid = UUID(document_id)
            
            # Get the document
            document = self.repository.get_document_by_id(doc_uuid)
            if not document:
                raise HTTPException(status_code=404, detail="Document not found")
            
            # Check if user has access to this document
            if document.user_id != user.id:
                raise HTTPException(status_code=403, detail="Access denied to this document")
            
            # Reset document status to PENDING for re-indexing
            from sentra_shared.domain.entities.document_entity import DocumentStatus
            document.status = DocumentStatus.PENDING
            document.error = None  # Clear any previous errors
            document.status_message = "Queued for re-indexing"
            
            # Save to database
            updated_document = self.repository.update_document(document)
            
            # Queue for indexing
            try:
                with self.indexing_publisher:
                    success = self.indexing_publisher.publish_indexing_job(
                        document_id=str(document.id),
                        document_path=document.path,
                        knowledge_source_id=str(document.knowledge_source_id),
                        filename=document.filename,
                        uploaded_by=str(user.id)
                    )
                    if success:
                        logger.info(f"Document {document_id} queued for re-indexing by user {user.id}")
                    else:
                        logger.warning(f"Failed to queue document {document_id} for re-indexing")
            except Exception as e:
                logger.error(f"Failed to queue document {document_id} for re-indexing: {e}")
                # Continue - document status is updated but indexing will need to be retried
            
            return updated_document
        except HTTPException as he:
            logger.error(f"HTTP error re-indexing document: {he.detail}")
            raise he
        except Exception as e:
            logger.error(f"Failed to re-index document: {e}")
            raise SentraHTTPException(
                status_code=500,
                code="REINDEX_DOCUMENT_FAILED",
                message="No se pudo reindexar el documento.",
                details=str(e),
                path="/knowledge/documents/reindex",
                suggestion="Revisa los permisos de acceso a la base de datos."
            )

    def remove_document(self, document_id: str, user: UserEntity) -> DocumentEntity:
        """Mark a document for removal"""
        try:
            from uuid import UUID
            doc_uuid = UUID(document_id)
            
            # Get the document
            document = self.repository.get_document_by_id(doc_uuid)
            if not document:
                raise HTTPException(status_code=404, detail="Document not found")
            
            # Check if user has access to this document
            if document.user_id != user.id:
                raise HTTPException(status_code=403, detail="Access denied to this document")
            
            # Set status to TO_BE_REMOVED
            from sentra_shared.domain.entities.document_entity import DocumentStatus
            document.status = DocumentStatus.TO_BE_REMOVED
            document.status_message = "Marked for removal"
            
            # Save to database
            updated_document = self.repository.update_document(document)
            logger.info(f"Document {document_id} marked for removal by user {user.id}")
            
            # TODO: Send message to sentra_rag_worker for actual deletion
            # This would be implemented when the worker supports removal operations
            
            return updated_document
        except HTTPException as he:
            logger.error(f"HTTP error removing document: {he.detail}")
            raise he
        except Exception as e:
            logger.error(f"Failed to remove document: {e}")
            raise SentraHTTPException(
                status_code=500,
                code="REMOVE_DOCUMENT_FAILED",
                message="No se pudo marcar el documento para eliminación.",
                details=str(e),
                path="/knowledge/documents/remove",
                suggestion="Revisa los permisos de acceso a la base de datos."
            )
