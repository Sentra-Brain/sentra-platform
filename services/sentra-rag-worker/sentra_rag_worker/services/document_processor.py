from pathlib import Path
from sentra_core.domain.entities.document_entity import DocumentFileType, DocumentStatus
from sentra_core.domain.services.file_storage import FileStorageService
from sentra_rag.embeddings.provider import get_embedding_provider
from sentra_rag_worker.services.document_extractor import DocumentExtractor
from sentra_rag_worker.services.text_chunker import TextChunker
from sentra_rag.vector_store.service import get_vector_store_service
from sentra_core.core.logging import get_logger, set_request_id
from sentra_core.domain.repository.knowledge_source_repository import KnowledgeSourceRepository
from sentra_core.domain.repository.document_repository import DocumentRepository
from sentra_core.infra.sql.postgres_service import create_db_session
from typing import Dict, Any, Optional
from uuid import UUID
import os
 
logger = get_logger(__name__)


class DocumentProcessor:
    """Main orchestrator for document processing pipeline.""" 

    def __init__(self):
        self.extractor = DocumentExtractor()
        self.chunker = TextChunker()
        self.embedding_service = get_embedding_provider()
        self.vector_store = get_vector_store_service()
        self._file_storage = None
    
    def _get_settings(self):
        """Lazy import of settings to avoid circular imports"""
        from sentra_core.core.settings import settings
        return settings
    
    def _get_file_storage(self) -> FileStorageService:
        """Lazy initialization of file storage service"""
        if self._file_storage is None:
            settings = self._get_settings()
            self._file_storage = FileStorageService(settings.knowledge_mount_path)
        return self._file_storage

    async def process_document(self, message: Dict[str, Any]) -> bool:
        """
        Processes a document through extraction, chunking, embedding, and storage.

        Args:
            message (Dict[str, Any]): Dictionary containing document metadata and file information.
                Expected keys: 'request_id', 'document_id', 'knowledge_source_id', 'filepath', 'filename', 'filetype'.

        Returns:
            bool: True if processing succeeds, False otherwise.
        """
        request_id = set_request_id(message.get('request_id'))
        document_id = UUID(message['document_id'])
        knowledge_source_id = UUID(message['knowledge_source_id'])
        filepath = message['filepath']
        filename = message['filename']
        filetype_str = message['filetype']

        logger.info(f"Processing document {document_id}: {filename}")

        try:
            filetype = DocumentFileType(filetype_str)
        except ValueError:
            self._set_status(document_id, DocumentStatus.FAILED, f"Unsupported file type: {filetype_str}")
            return False

        db = create_db_session()
        try:
            document_repo = DocumentRepository(db)
            file_storage = self._get_file_storage()

            self._set_status(document_id, DocumentStatus.PROCESSING, repo=document_repo)

            try:
                absolute_filepath = file_storage.resolve_document_path(filepath)
            except ValueError as e:
                return self._fail(document_id, str(e), repo=document_repo)

            if not self._validate_file(str(absolute_filepath)):
                return self._fail(document_id, f"Invalid file: {absolute_filepath}", repo=document_repo)

            self._set_status(document_id, DocumentStatus.EXTRACTING, repo=document_repo)
            try:
                content = self.extractor.extract_content(str(absolute_filepath), filetype)
                if not content.strip():
                    return self._fail(document_id, "No content extracted", repo=document_repo)
            except Exception as e:
                return self._fail(document_id, f"Extraction failed: {e}", repo=document_repo)

            self._set_status(document_id, DocumentStatus.CHUNKING, repo=document_repo)
            try:
                chunks = self.chunker.chunk_text(content)
                if not chunks:
                    return self._fail(document_id, "No chunks generated", repo=document_repo)
            except Exception as e:
                return self._fail(document_id, f"Chunking failed: {e}", repo=document_repo)

            self._set_status(document_id, DocumentStatus.EMBEDDING, repo=document_repo)
            try:
                embeddings = self.embedding_service.generate_embeddings(chunks)
                if len(embeddings) != len(chunks):
                    return self._fail(document_id, "Embedding count mismatch", repo=document_repo)
            except Exception as e:
                return self._fail(document_id, f"Embedding failed: {e}", repo=document_repo)

            self._set_status(document_id, DocumentStatus.INDEXING, repo=document_repo)
            try:
                indexed = await self.vector_store.index_document_chunks(
                    document_id=document_id,
                    knowledge_source_id=knowledge_source_id,
                    chunks=chunks,
                    embeddings=embeddings,
                    filename=filename,
                    source_type="file"
                )
                if indexed != len(chunks):
                    return self._fail(document_id, f"Indexed only {indexed}/{len(chunks)} chunks", repo=document_repo)
            except Exception as e:
                return self._fail(document_id, f"Indexing failed: {e}", repo=document_repo)

            self._set_status(document_id, DocumentStatus.INDEXED, repo=document_repo, chunks_count=len(chunks))
            logger.info(f"Document {document_id} processed successfully.")
            return True

        except Exception as e:
            self._set_status(document_id, DocumentStatus.FAILED, f"Unexpected error: {e}")
            return False
        finally:
            db.close()

    def _set_status(
        self, 
        document_id: UUID, 
        status: DocumentStatus, 
        error: Optional[str] = None, 
        chunks_count: Optional[int] = None, 
        repo: Optional[DocumentRepository] = None
    ):
        try:
            if not repo:
                db = create_db_session()
                repo = DocumentRepository(db)
                repo.update_status(document_id, status, error, None, chunks_count)
                db.close()
            else:
                repo.update_status(document_id, status, error, None, chunks_count)
            logger.info(f"Status of document {document_id} set to {status.value}")
        except Exception as e:
            logger.error(f"Failed to update document status to {status.value}: {e}")

    def _fail(self, document_id: UUID, error: str, repo: DocumentRepository) -> bool:
        logger.error(error)
        self._set_status(document_id, DocumentStatus.FAILED, error, repo=repo)
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