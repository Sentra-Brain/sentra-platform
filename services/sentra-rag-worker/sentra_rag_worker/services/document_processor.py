from pathlib import Path
from sentra.domain.entities.document_entity import DocumentFileType, DocumentStatus
from sentra.domain.services.file_storage import FileStorageService
from sentra.rag.embeddings.provider import get_embedding_provider
from sentra_rag_worker.services.extraction import get_extractor
from sentra_rag_worker.services.sanitizer import cast_to_markdown
from sentra_rag_worker.services.metadata import extract_metadata
from sentra_rag_worker.services.text_chunker import TextChunker
from sentra.rag.vector_store.service import get_vector_store_service
from sentra.shared.logging import get_logger, set_request_id
from sentra.domain.repository.knowledge_source_repository import KnowledgeSourceRepository
from sentra.domain.repository.document_repository import DocumentRepository
from sentra.infra.sql.postgres_service import create_db_session
from typing import Dict, Any, Optional
from uuid import UUID
import os
 
logger = get_logger(__name__)


class DocumentProcessor:
    """Main orchestrator for document processing pipeline.""" 

    def __init__(self):
        self.chunker = TextChunker()
        self.embedding_service = get_embedding_provider()
        self.vector_store = get_vector_store_service()
        self._file_storage = None
    
    def _get_settings(self):
        """Lazy import of settings to avoid circular imports"""
        from sentra.shared.settings import settings
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

            def fail(reason: str) -> bool:
                return self._fail(document_id, reason, repo=document_repo)

            self._set_status(document_id, DocumentStatus.PROCESSING, repo=document_repo)

            try:
                absolute_filepath = file_storage.resolve_document_path(filepath)
            except ValueError as e:
                return fail(str(e))

            if not self._validate_file(str(absolute_filepath)):
                return fail(f"Invalid file: {absolute_filepath}")

            # --- Step 1: Extract text ---
            self._set_status(document_id, DocumentStatus.EXTRACTING, repo=document_repo)
            try:
                extractor = get_extractor(filetype)
                payload = extractor.extract(str(absolute_filepath))

                if not payload.raw_text or not payload.raw_text.strip():
                    return fail("No content extracted")

                logger.info(f"Extracted {len(payload.raw_text)} characters, {payload.word_count} words")
            except Exception as e:
                return fail(f"Extraction failed: {e}")

            # --- Step 2: Cast to Markdown ---
            self._set_status(document_id, DocumentStatus.PROCESSING, "Casting to markdown", repo=document_repo)
            try:
                text_md = extractor.extract_markdown(str(absolute_filepath))

                if not text_md.strip():
                    return fail("Markdown casting produced no content")

                metadata = extract_metadata(payload, text_md, filetype, str(absolute_filepath), filename)

                logger.info(f"Cast to markdown: {len(text_md)} characters, detected title: {metadata.get('extracted_title')}")
            except Exception as e:
                return fail(f"Markdown casting failed: {e}")

            # --- Step 3: Persist Markdown if configured ---
            try:
                if self._get_settings().persist_markdown:
                    path, size, sha256 = file_storage.save_markdown(
                        document_id=document_id,
                        markdown=text_md
                    )
                    document_repo.update_markdown_info(
                        document_id=document_id,
                        path=path,
                        size=size,
                        sha256=sha256
                    )
            except Exception as e:
                logger.warning(f"Failed to persist markdown for {document_id}: {e}")

            # --- Step 4: Chunk text ---
            self._set_status(document_id, DocumentStatus.CHUNKING, repo=document_repo)
            try:
                chunks = self.chunker.chunk_text(text_md, filetype)
                if not chunks:
                    return fail("No chunks generated")
                logger.info(f"Generated {len(chunks)} chunks using adaptive strategy for {filetype.value}")
            except Exception as e:
                return fail(f"Chunking failed: {e}")

            # --- Step 5: Generate embeddings ---
            self._set_status(document_id, DocumentStatus.EMBEDDING, repo=document_repo)
            try:
                embeddings = self.embedding_service.generate_embeddings(chunks)
                if len(embeddings) != len(chunks):
                    return fail("Embedding count mismatch")
            except Exception as e:
                return fail(f"Embedding failed: {e}")

            # --- Step 6: Index chunks ---
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
                    return fail(f"Indexed only {indexed}/{len(chunks)} chunks")
            except Exception as e:
                return fail(f"Indexing failed: {e}")

            # --- Done ---
            self._set_status(
                document_id,
                DocumentStatus.INDEXED,
                repo=document_repo,
                chunks_count=len(chunks),
                metadata=metadata
            )
            logger.info(f"Document {document_id} processed successfully with {len(chunks)} chunks.")
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
        metadata: Optional[Dict[str, Any]] = None,
        repo: Optional[DocumentRepository] = None
    ):
        try:
            if not repo:
                db = create_db_session()
                repo = DocumentRepository(db)
                
                # Enhanced status update with metadata
                self._update_document_with_metadata(repo, document_id, status, error, chunks_count, metadata)
                
                db.close()
            else:
                self._update_document_with_metadata(repo, document_id, status, error, chunks_count, metadata)
                
            logger.info(f"Status of document {document_id} set to {status.value}")
        except Exception as e:
            logger.error(f"Failed to update document status to {status.value}: {e}")

    def _update_document_with_metadata(
        self,
        repo: DocumentRepository,
        document_id: UUID,
        status: DocumentStatus,
        error: Optional[str],
        chunks_count: Optional[int],
        metadata: Optional[Dict[str, Any]]
    ):
        """Update document with status and enriched metadata."""
        # For now, use the existing update_status method
        # In a future enhancement, we could extend the repository to handle metadata
        status_message = None
        
        if metadata and status == DocumentStatus.INDEXED:
            # Create a summary status message with key metadata
            extracted_title = metadata.get('extracted_title')
            word_count = metadata.get('word_count')
            language = metadata.get('language')
            page_count = metadata.get('page_count')
            
            status_parts = []
            if extracted_title:
                status_parts.append(f"title: {extracted_title}")
            if word_count:
                status_parts.append(f"{word_count} words")
            if page_count:
                status_parts.append(f"{page_count} pages")
            if language:
                status_parts.append(f"lang: {language}")
                
            if status_parts:
                status_message = ", ".join(status_parts)
        
        repo.update_status(document_id, status, error, status_message, chunks_count)

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