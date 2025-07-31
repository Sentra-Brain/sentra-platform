# sentra_core/domain/services/document_service.py
from uuid import UUID
from sentra_core.domain.entities.document_entity import DocumentEntity, DocumentStatus
from sentra_core.domain.repository.document_repository import DocumentRepository

class DocumentService:
    def __init__(self, repository: DocumentRepository):
        self.repository = repository

    def mark_for_reindex(self, document_id: UUID, user_id: UUID) -> DocumentEntity:
        doc = self.repository.get(document_id)
        if not doc:
            raise ValueError("Document not found")
        if doc.created_by_id != user_id:
            raise PermissionError("Not allowed to reindex this document")
        doc.status = DocumentStatus.PENDING
        doc.error = None
        doc.status_message = "Queued for reindexing"
        return self.repository.update(doc)

    def mark_for_removal(self, document_id: UUID, user_id: UUID) -> DocumentEntity:
        doc = self.repository.get(document_id)
        if not doc:
            raise ValueError("Document not found")
        if doc.created_by_id != user_id:
            raise PermissionError("Not allowed to remove this document")
        doc.status = DocumentStatus.TO_BE_REMOVED
        doc.status_message = "Marked for removal"
        return self.repository.update(doc)
