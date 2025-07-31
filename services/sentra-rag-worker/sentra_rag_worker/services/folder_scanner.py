import os
from pathlib import Path
from typing import List, Dict, Any
from uuid import UUID, uuid4
from sentra_core.core.logging import get_logger
from sentra_rag_worker.core.config import settings
from sentra_core.domain.entities.document_entity import DocumentEntity, DocumentFileType, DocumentStatus
from sentra_core.domain.entities.knowledge_source_entity import KnowledgeSourceEntity
from sentra_core.domain.repository.knowledge_source_repository import KnowledgeRepository

logger = get_logger(__name__)


class FolderScanner:
    """Scan folder-type knowledge sources for new or changed files."""

    # Supported file extensions
    SUPPORTED_EXTENSIONS = {
        '.pdf': DocumentFileType.PDF,
        '.docx': DocumentFileType.DOCX,
        '.txt': DocumentFileType.TXT,
        '.md': DocumentFileType.MD
    }

    def __init__(self, repo: KnowledgeRepository):
        self.repo = repo

    def scan_folder_sources(self) -> List[Dict[str, Any]]:
        """Scan all folder knowledge sources for new files.
        
        Returns:
            List of indexation jobs to be queued
        """
        jobs = []
        
        try:
            # Get all folder-type knowledge sources with auto_index enabled
            folder_sources = self.repo.get_folder_knowledge_sources(auto_index_only=True)
            
            logger.info(f"Scanning {len(folder_sources)} folder knowledge sources")
            
            for source in folder_sources:
                try:
                    source_jobs = self._scan_single_folder(source)
                    jobs.extend(source_jobs)
                except Exception as e:
                    logger.error(f"Error scanning folder {source.path}: {e}")
                    continue
            
            logger.info(f"Found {len(jobs)} new files to index")
            return jobs
            
        except Exception as e:
            logger.error(f"Error during folder scanning: {e}")
            return []

    def _scan_single_folder(self, source: KnowledgeSourceEntity) -> List[Dict[str, Any]]:
        """Scan a single folder knowledge source.
        
        Args:
            source: The knowledge source to scan
            
        Returns:
            List of indexation jobs for new files
        """
        jobs = []
        
        if not source.path:
            logger.warning(f"Knowledge source {source.id} has no path configured")
            return jobs

        # Resolve the full path
        folder_path = self._resolve_folder_path(source.path)
        
        if not folder_path.exists():
            logger.warning(f"Folder does not exist: {folder_path}")
            return jobs

        if not folder_path.is_dir():
            logger.warning(f"Path is not a directory: {folder_path}")
            return jobs

        # Get existing documents for this knowledge source
        existing_docs = self.repo.list_documents_by_knowledge_source(source.id)
        existing_paths = {doc.path for doc in existing_docs}

        # Recursively scan the folder
        discovered_files = self._discover_files(folder_path)
        
        logger.info(f"Discovered {len(discovered_files)} supported files in {folder_path}")

        for file_path in discovered_files:
            file_path_str = str(file_path)
            
            # Skip if already in database
            if file_path_str in existing_paths:
                continue

            # Create new document entry and job
            try:
                job = self._create_indexation_job(file_path, source)
                if job:
                    jobs.append(job)
            except Exception as e:
                logger.error(f"Error creating job for {file_path}: {e}")
                continue

        return jobs

    def _resolve_folder_path(self, source_path: str) -> Path:
        """Resolve the full folder path."""
        # If absolute path, use as-is
        if os.path.isabs(source_path):
            return Path(source_path)
        
        # Otherwise, resolve relative to knowledge root
        return Path(settings.knowledge_root) / source_path

    def _discover_files(self, folder_path: Path) -> List[Path]:
        """Recursively discover supported files in the folder."""
        files = []
        
        try:
            for item in folder_path.rglob('*'):
                # Skip directories
                if not item.is_file():
                    continue
                
                # Skip hidden files and system files
                if any(part.startswith('.') for part in item.parts):
                    continue
                
                # Check if file extension is supported
                extension = item.suffix.lower()
                if extension in self.SUPPORTED_EXTENSIONS:
                    files.append(item)
                    
        except Exception as e:
            logger.error(f"Error discovering files in {folder_path}: {e}")
        
        return files

    def _create_indexation_job(self, file_path: Path, source: KnowledgeSourceEntity) -> Dict[str, Any]:
        """Create a new document entry and indexation job.
        
        Args:
            file_path: Path to the file
            source: The knowledge source
            
        Returns:
            Indexation job dictionary or None if creation failed
        """
        try:
            # Get file info
            file_path_str = str(file_path)
            filename = file_path.name
            extension = file_path.suffix.lower()
            filetype = self.SUPPORTED_EXTENSIONS[extension]
            
            # Create new document entity
            document = DocumentEntity(
                id=uuid4(),
                filename=filename,
                display_name=filename,
                filetype=filetype,
                path=file_path_str,
                uploaded_by=source.user_id,  # Use the source creator as uploader
                status=DocumentStatus.PENDING,
                knowledge_source_id=source.id
            )
            
            # Save to database
            created_doc = self.repo.create_document(document)
            
            # Create indexation job message
            job = {
                "document_id": str(created_doc.id),
                "knowledge_source_id": str(source.id),
                "filepath": file_path_str,
                "filename": filename,
                "display_name": filename,
                "uploaded_by": str(source.user_id),
                "filetype": filetype.value
            }
            
            logger.info(f"Created indexation job for new file: {filename}")
            return job
            
        except Exception as e:
            logger.error(f"Failed to create indexation job for {file_path}: {e}")
            return None

    def detect_missing_files(self) -> List[UUID]:
        """Detect documents whose files no longer exist.
        
        Returns:
            List of document IDs that should be marked as missing/failed
        """
        missing_docs = []
        
        try:
            # Get all folder sources
            folder_sources = self.repo.get_folder_knowledge_sources(auto_index_only=False)
            
            for source in folder_sources:
                try:
                    docs = self.repo.list_documents_by_knowledge_source(source.id)
                    
                    for doc in docs:
                        # Skip documents that are already failed
                        if doc.status == DocumentStatus.FAILED:
                            continue
                            
                        # Check if file still exists
                        if not os.path.exists(doc.path):
                            missing_docs.append(doc.id)
                            logger.info(f"File no longer exists: {doc.path}")
                            
                except Exception as e:
                    logger.error(f"Error checking files for source {source.id}: {e}")
                    continue
            
            logger.info(f"Found {len(missing_docs)} missing files")
            return missing_docs
            
        except Exception as e:
            logger.error(f"Error detecting missing files: {e}")
            return []

    def mark_missing_files_as_failed(self, missing_doc_ids: List[UUID]) -> int:
        """Mark missing documents as failed.
        
        Args:
            missing_doc_ids: List of document IDs to mark as failed
            
        Returns:
            Number of documents marked as failed
        """
        marked_count = 0
        
        for doc_id in missing_doc_ids:
            try:
                self.repo.update_document_status(
                    doc_id, 
                    DocumentStatus.FAILED, 
                    error="File no longer exists"
                )
                marked_count += 1
            except Exception as e:
                logger.error(f"Failed to mark document {doc_id} as failed: {e}")
        
        if marked_count > 0:
            logger.info(f"Marked {marked_count} missing files as failed")
        
        return marked_count