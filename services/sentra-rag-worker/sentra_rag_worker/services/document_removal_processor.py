"""
Document removal processor for handling document deletion jobs.

This processor handles the complete removal workflow:
1. Update document status to TO_BE_REMOVED
2. Remove from ChromaDB vector store  
3. Remove file from disk
4. Update document status to REMOVED or FAILED
"""

import os
from typing import Dict, Any
from uuid import UUID
from sentra_rag_worker.services.vector_store_service import VectorStoreService
from sentra_shared.core.logging import get_logger
from sentra_shared.domain.entities.document_entity import DocumentEntity
from sentra_shared.domain.enums.document import DocumentStatus
from sentra_shared.infra.sql.postgres_service import create_db_session

logger = get_logger(__name__)


class DocumentRemovalProcessor:
    """
    Processor for handling document removal jobs.
    
    Manages the complete lifecycle of document removal including
    vector store cleanup, file deletion, and status tracking.
    """

    def __init__(self):
        self.vector_store = VectorStoreService()

    def process_removal_job(self, message: Dict[str, Any]) -> bool:
        """
        Process a document removal job.
        
        Args:
            message: Removal job message containing document_id, knowledge_source_id, user_id
            
        Returns:
            True if removal was successful, False otherwise
        """
        try:
            # Extract job parameters
            document_id = UUID(message['document_id'])
            knowledge_source_id = UUID(message['knowledge_source_id']) 
            user_id = UUID(message['user_id'])

            logger.info(f"Starting removal process for document {document_id}")

            # Step 1: Update document status to TO_BE_REMOVED
            if not self._update_document_status(document_id, DocumentStatus.TO_BE_REMOVED):
                logger.error(f"Failed to update document {document_id} status to TO_BE_REMOVED")
                return False

            # Step 2: Get document details for file path
            document = self._get_document(document_id)
            if not document:
                logger.error(f"Document {document_id} not found in database")
                self._update_document_status(document_id, DocumentStatus.FAILED, "Document not found")
                return False

            # Step 3: Remove from ChromaDB vector store
            try:
                deleted_chunks = self.vector_store.delete_document_chunks(document_id)
                logger.info(f"Removed {deleted_chunks} chunks from vector store for document {document_id}")
            except Exception as e:
                logger.warning(f"Failed to remove chunks from vector store for document {document_id}: {e}")
                # Continue with file deletion even if vector store cleanup fails

            # Step 4: Remove file from disk
            try:
                if self._remove_file_from_disk(document.path):
                    logger.info(f"Removed file from disk: {document.path}")
                else:
                    logger.warning(f"File not found or already removed: {document.path}")
            except Exception as e:
                logger.warning(f"Failed to remove file from disk {document.path}: {e}")
                # Continue to mark as removed even if file deletion fails

            # Step 5: Update document status to REMOVED
            if self._update_document_status(document_id, DocumentStatus.REMOVED):
                logger.info(f"Successfully completed removal of document {document_id}")
                return True
            else:
                logger.error(f"Failed to update final status for document {document_id}")
                return False

        except Exception as e:
            logger.error(f"Unexpected error during removal of document {message.get('document_id', 'unknown')}: {e}")
            # Try to mark as failed if we have a valid document_id
            try:
                if 'document_id' in message:
                    document_id = UUID(message['document_id'])
                    self._update_document_status(document_id, DocumentStatus.FAILED, str(e))
            except:
                pass  # Best effort
            return False

    def _get_document(self, document_id: UUID) -> DocumentEntity:
        """Get document from database."""
        db = None
        try:
            db = create_db_session()
            return db.query(DocumentEntity).filter(DocumentEntity.id == document_id).first()
        except Exception as e:
            logger.error(f"Failed to get document {document_id} from database: {e}")
            return None
        finally:
            if db:
                db.close()

    def _update_document_status(self, document_id: UUID, status: DocumentStatus, error_message: str = None) -> bool:
        """Update document status in database."""
        db = None
        try:
            db = create_db_session()
            document = db.query(DocumentEntity).filter(DocumentEntity.id == document_id).first()
            
            if not document:
                logger.error(f"Document {document_id} not found for status update")
                return False

            document.status = status
            if error_message:
                document.error = error_message
            
            db.commit()
            logger.info(f"Updated document {document_id} status to {status.value}")
            return True

        except Exception as e:
            logger.error(f"Failed to update document {document_id} status to {status.value}: {e}")
            if db:
                db.rollback()
            return False
        finally:
            if db:
                db.close()

    def _remove_file_from_disk(self, file_path: str) -> bool:
        """
        Remove file from disk.
        
        Args:
            file_path: Path to the file to remove
            
        Returns:
            True if file was removed or didn't exist, False on error
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Removed file from disk: {file_path}")
                return True
            else:
                logger.info(f"File not found (already removed?): {file_path}")
                return True  # Consider success if file doesn't exist
        except Exception as e:
            logger.error(f"Failed to remove file {file_path}: {e}")
            return False