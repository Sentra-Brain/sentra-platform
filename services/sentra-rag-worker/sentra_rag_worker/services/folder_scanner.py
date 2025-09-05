# services/sentra-rag-worker/sentra_rag_worker/services/folder_scanner.py
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from uuid import UUID, uuid4

from sentra.shared.logging import get_logger
from sentra.domain.entities.document_entity import DocumentEntity, DocumentFileType, DocumentStatus
from sentra.domain.entities.knowledge_source_entity import KnowledgeSourceEntity
from sentra.domain.repository.document_repository import DocumentRepository
from sentra.domain.repository.knowledge_source_repository import KnowledgeSourceRepository
from sentra_rag_worker.core.config import settings

logger = get_logger(__name__)


class FolderScanner:
    """Scan folder-type knowledge sources for new or missing files."""

    SUPPORTED_EXTENSIONS = {
        '.pdf': DocumentFileType.PDF,
        '.docx': DocumentFileType.DOCX,
        '.txt': DocumentFileType.TXT,
        '.md': DocumentFileType.MD,
    }

    def __init__(
        self,
        source_repo: KnowledgeSourceRepository,
        document_repo: DocumentRepository
    ):
        self.source_repo = source_repo
        self.document_repo = document_repo

    def scan_folder_sources(self) -> List[Dict[str, Any]]:
        """Scan all folder-type sources with auto_index for new files."""
        jobs = []
        try:
            folder_sources = self.source_repo.get_folder_sources(auto_index_only=True)
            logger.info(f"📁 Scanning {len(folder_sources)} folder knowledge sources")

            for source in folder_sources:
                try:
                    jobs += self._scan_single_folder(source)
                except Exception as e:
                    logger.error(f"❌ Error scanning folder {source.path}: {e}")
                    continue

            logger.info(f"✅ Found {len(jobs)} new files to index")
            return jobs
        except Exception as e:
            logger.error(f"❌ Error during folder scanning: {e}")
            return []

    def _scan_single_folder(self, source: KnowledgeSourceEntity) -> List[Dict[str, Any]]:
        """Scan a single folder and return indexation jobs for new files."""
        jobs = []

        if not source.path:
            logger.warning(f"⚠️ Knowledge source {source.id} has no path configured")
            return jobs

        folder_path = self._resolve_folder_path(source.path)

        if not folder_path.exists() or not folder_path.is_dir():
            logger.warning(f"⚠️ Invalid folder path: {folder_path}")
            return jobs

        existing_docs = self.document_repo.list_by_source(source.id)
        existing_paths = {doc.path for doc in existing_docs}

        discovered_files = self._discover_files(folder_path)
        logger.info(f"🔍 Discovered {len(discovered_files)} supported files in {folder_path}")

        for file_path in discovered_files:
            file_path_str = str(file_path)

            if file_path_str in existing_paths:
                continue

            try:
                job = self._create_document_and_job(file_path, source)
                if job:
                    jobs.append(job)
            except Exception as e:
                logger.error(f"❌ Error creating job for {file_path_str}: {e}")
                continue

        return jobs

    def _create_document_and_job(self, file_path: Path, source: KnowledgeSourceEntity) -> Optional[Dict[str, Any]]:
        """Create and persist a new document, return the indexation job dict."""
        extension = file_path.suffix.lower()
        if extension not in self.SUPPORTED_EXTENSIONS:
            return None

        filetype = self.SUPPORTED_EXTENSIONS[extension]
        file_path_str = str(file_path)
        filename = file_path.name

        document = DocumentEntity(
            id=uuid4(),
            filename=filename,
            display_name=filename,
            filetype=filetype,
            path=file_path_str,
            uploaded_by=source.created_by_id,
            status=DocumentStatus.PENDING,
            knowledge_source_id=source.id
        )

        created = self.document_repo.create(document)

        job = {
            "document_id": str(created.id),
            "knowledge_source_id": str(source.id),
            "filepath": file_path_str,
            "filename": filename,
            "display_name": filename,
            "uploaded_by": str(source.created_by_id),
            "filetype": filetype.value
        }

        logger.info(f"📄 Created job for file: {filename}")
        return job

    def _resolve_folder_path(self, source_path: str) -> Path:
        """Resolve folder path relative to knowledge root."""
        if os.path.isabs(source_path):
            return Path(source_path)
        return Path(settings.knowledge_root) / source_path

    def _discover_files(self, folder_path: Path) -> List[Path]:
        """Recursively find supported files."""
        files = []
        try:
            for item in folder_path.rglob('*'):
                if not item.is_file():
                    continue
                if any(part.startswith('.') for part in item.parts):
                    continue
                if item.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                    files.append(item)
        except Exception as e:
            logger.error(f"❌ Error discovering files in {folder_path}: {e}")
        return files

    def detect_missing_files(self) -> List[UUID]:
        """Detect documents pointing to non-existent files."""
        missing = []

        try:
            folder_sources = self.source_repo.get_folder_sources(auto_index_only=False)
            for source in folder_sources:
                try:
                    docs = self.document_repo.list_by_source(source.id)
                    for doc in docs:
                        if doc.status == DocumentStatus.FAILED:
                            continue
                        if not os.path.exists(doc.path):
                            logger.info(f"🚫 Missing file: {doc.path}")
                            missing.append(doc.id)
                except Exception as e:
                    logger.error(f"Error checking source {source.id}: {e}")
        except Exception as e:
            logger.error(f"❌ Error detecting missing files: {e}")

        logger.info(f"🧹 Found {len(missing)} missing documents")
        return missing

    def mark_missing_files_as_failed(self, missing_doc_ids: List[UUID]) -> int:
        """Update missing documents' status to FAILED."""
        count = 0
        for doc_id in missing_doc_ids:
            try:
                self.document_repo.update_status(
                    document_id=doc_id,
                    status=DocumentStatus.FAILED,
                    error="File no longer exists"
                )
                count += 1
            except Exception as e:
                logger.error(f"❌ Failed to mark document {doc_id} as failed: {e}")

        if count:
            logger.info(f"✅ Marked {count} documents as FAILED")
        return count
