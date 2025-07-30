from pathlib import Path
from sentra_shared.domain.entities.document_entity import DocumentFileType, DocumentStatus
from sentra_shared.domain.services.file_storage import FileStorageService
from sentra_rag_worker.services.document_extractor import DocumentExtractor
from sentra_rag_worker.services.embedding_service import EmbeddingService
from sentra_rag_worker.services.text_chunker import TextChunker
from sentra_rag_worker.services.vector_store_service import VectorStoreService
from sentra_shared.core.logging import get_logger, set_request_id
from sentra_shared.domain.repository.knowledge_source_repository import KnowledgeRepository
from sentra_shared.infra.sql.postgres_service import create_db_session
from typing import Dict, Any
from uuid import UUID
import os

logger = get_logger(__name__)


class DocumentProcessor:
    """Main orchestrator for document processing pipeline."""

    def __init__(self):
        self.extractor = DocumentExtractor()
        self.chunker = TextChunker()
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStoreService()
        self._file_storage = None
    
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

    def process_document(self, message: Dict[str, Any]) -> bool:
        """Process a document indexation job.
        
        Args:
            message: Message from RabbitMQ containing document details
            
        Returns:
            True if processing was successful, False otherwise
        """
        try:
            # Set up request context for tracing
            request_id = set_request_id(message.get('request_id'))
            
            # Extract message fields
            document_id = UUID(message['document_id'])
            knowledge_source_id = UUID(message['knowledge_source_id'])
            filepath = message['filepath']  # This should be relative path
            filename = message['filename']
            display_name = message.get('display_name', filename)
            filetype_str = message['filetype']
            
            logger.info(f"Processing document {document_id}: {filename}")

            # Validate file type
            try:
                filetype = DocumentFileType(filetype_str)
            except ValueError:
                logger.error(f"Unsupported file type: {filetype_str}")
                self._update_document_status(document_id, DocumentStatus.FAILED, f"Unsupported file type: {filetype_str}")
                return False

            # Create database session
            db = create_db_session()
            try:
                repo = KnowledgeRepository(db)
                
                # Update status to processing
                self._update_document_status_with_repo(repo, document_id, DocumentStatus.PROCESSING)

                # Resolve relative path to absolute path using FileStorageService
                file_storage = self._get_file_storage()
                try:
                    absolute_filepath = file_storage.resolve_document_path(filepath)
                except ValueError as e:
                    error_msg = f"Path resolution failed: {e}"
                    logger.error(error_msg)
                    self._update_document_status_with_repo(repo, document_id, DocumentStatus.FAILED, error_msg)
                    return False

                # Step 1: Validation using absolute path
                if not self._validate_file(str(absolute_filepath)):
                    error_msg = f"File validation failed: {absolute_filepath}"
                    logger.error(error_msg)
                    self._update_document_status_with_repo(repo, document_id, DocumentStatus.FAILED, error_msg)
                    return False

                # Step 2: Content extraction
                self._update_document_status_with_repo(repo, document_id, DocumentStatus.EXTRACTING)
                logger.info("extracting")
                try:
                    content = self.extractor.extract_content(str(absolute_filepath), filetype)
                    if not content.strip():
                        error_msg = "No content extracted from document"
                        logger.warning(error_msg)
                        self._update_document_status_with_repo(repo, document_id, DocumentStatus.FAILED, error_msg)
                        return False
                except Exception as e:
                    error_msg = f"Content extraction failed: {str(e)}"
                    logger.error(error_msg)
                    self._update_document_status_with_repo(repo, document_id, DocumentStatus.FAILED, error_msg)
                    return False

                # Step 3: Text chunking
                self._update_document_status_with_repo(repo, document_id, DocumentStatus.CHUNKING)
                logger.info("chunking")
                try:
                    chunks = self.chunker.chunk_text(content)
                    if not chunks:
                        error_msg = "No chunks generated from content"
                        logger.warning(error_msg)
                        self._update_document_status_with_repo(repo, document_id, DocumentStatus.FAILED, error_msg)
                        return False
                    
                    logger.info(f"Generated {len(chunks)} chunks for document {document_id}")
                except Exception as e:
                    error_msg = f"Text chunking failed: {str(e)}"
                    logger.error(error_msg)
                    self._update_document_status_with_repo(repo, document_id, DocumentStatus.FAILED, error_msg)
                    return False

                # Step 4: Generate embeddings
                self._update_document_status_with_repo(repo, document_id, DocumentStatus.EMBEDDING)
                logger.info("embedding")
                try:
                    embeddings = self.embedding_service.generate_embeddings(chunks)
                    if len(embeddings) != len(chunks):
                        error_msg = "Embedding count mismatch with chunk count"
                        logger.error(error_msg)
                        self._update_document_status_with_repo(repo, document_id, DocumentStatus.FAILED, error_msg)
                        return False
                except Exception as e:
                    error_msg = f"Embedding generation failed: {str(e)}"
                    logger.error(error_msg)
                    self._update_document_status_with_repo(repo, document_id, DocumentStatus.FAILED, error_msg)
                    return False

                # Step 5: Index into ChromaDB
                self._update_document_status_with_repo(repo, document_id, DocumentStatus.INDEXING)
                logger.info("indexing")
                try:
                    chunks_indexed = self.vector_store.index_document_chunks(
                        document_id=document_id,
                        knowledge_source_id=knowledge_source_id,
                        chunks=chunks,
                        embeddings=embeddings,
                        filename=filename,
                        source_type="file"
                    )
                    
                    if chunks_indexed != len(chunks):
                        error_msg = f"Indexing incomplete: {chunks_indexed}/{len(chunks)} chunks indexed"
                        logger.warning(error_msg)
                        self._update_document_status_with_repo(repo, document_id, DocumentStatus.FAILED, error_msg)
                        return False
                        
                except Exception as e:
                    error_msg = f"Vector indexing failed: {str(e)}"
                    logger.error(error_msg)
                    self._update_document_status_with_repo(repo, document_id, DocumentStatus.FAILED, error_msg)
                    return False

                # Step 6: Update document status to indexed
                self._update_document_status_with_repo(
                    repo, 
                    document_id, 
                    DocumentStatus.INDEXED, 
                    chunks_count=len(chunks)
                )

                logger.info(f"Successfully processed document {document_id}: {len(chunks)} chunks indexed")
                return True

            finally:
                db.close()

        except Exception as e:
            logger.error(f"Unexpected error processing document: {e}")
            try:
                self._update_document_status(
                    UUID(message.get('document_id', '00000000-0000-0000-0000-000000000000')),
                    DocumentStatus.FAILED,
                    f"Unexpected error: {str(e)}"
                )
            except:
                pass  # Don't let status update failures crash the processor
            return False

    def _validate_file(self, filepath: str) -> bool:
        """Validate that the file exists and is readable."""
        try:
            path = Path(filepath)
            
            # Check if file exists
            if not path.exists():
                logger.error(f"File does not exist: {filepath}")
                return False
            
            # Check if it's a file (not directory)
            if not path.is_file():
                logger.error(f"Path is not a file: {filepath}")
                return False
            
            # Check if file is readable
            if not os.access(filepath, os.R_OK):
                logger.error(f"File is not readable: {filepath}")
                return False
            
            # Check file size (optional: reject empty files)
            if path.stat().st_size == 0:
                logger.error(f"File is empty: {filepath}")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"File validation error: {e}")
            return False

    def _update_document_status(self, document_id: UUID, status: DocumentStatus, error: str = None, chunks_count: int = None):
        """Update document status using a new database session."""
        db = create_db_session()
        try:
            repo = KnowledgeRepository(db)
            self._update_document_status_with_repo(repo, document_id, status, error, chunks_count)
        finally:
            db.close()

    def _update_document_status_with_repo(
        self, 
        repo: KnowledgeRepository, 
        document_id: UUID, 
        status: DocumentStatus, 
        error: str = None, 
        chunks_count: int = None
    ):
        """Update document status using provided repository."""
        try:
            repo.update_document_status(document_id, status, error, chunks_count)
            logger.info(f"Updated document {document_id} status to {status.value}")
        except Exception as e:
            logger.error(f"Failed to update document status: {e}")