from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sentra_rag_worker.domain.knowledge_source_entity import KnowledgeSourceEntity, KnowledgeSourceType, KnowledgeSourceStatus
from sentra_rag_worker.domain.document_entity import DocumentEntity, DocumentStatus


class KnowledgeRepository:
    def __init__(self, db: Session):
        self.db = db

    # Knowledge Source methods
    def get_knowledge_source_by_id(self, source_id: UUID) -> Optional[KnowledgeSourceEntity]:
        return self.db.query(KnowledgeSourceEntity).filter(KnowledgeSourceEntity.id == source_id).first()

    def get_folder_knowledge_sources(self, auto_index_only: bool = True) -> List[KnowledgeSourceEntity]:
        """Get folder-type knowledge sources for scanning"""
        query = self.db.query(KnowledgeSourceEntity).filter(
            KnowledgeSourceEntity.type == KnowledgeSourceType.FOLDER,
            KnowledgeSourceEntity.status == KnowledgeSourceStatus.ACTIVE
        )
        if auto_index_only:
            query = query.filter(KnowledgeSourceEntity.auto_index == True)
        return query.all()

    # Document methods
    def create_document(self, document: DocumentEntity) -> DocumentEntity:
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document

    def get_document_by_id(self, document_id: UUID) -> Optional[DocumentEntity]:
        return self.db.query(DocumentEntity).filter(DocumentEntity.id == document_id).first()

    def get_document_by_path(self, filepath: str) -> Optional[DocumentEntity]:
        """Find document by file path for folder scanning"""
        return self.db.query(DocumentEntity).filter(DocumentEntity.path == filepath).first()

    def update_document_status(self, document_id: UUID, status: DocumentStatus, error: Optional[str] = None, chunks_count: Optional[int] = None) -> Optional[DocumentEntity]:
        document = self.get_document_by_id(document_id)
        if document:
            document.status = status
            if error:
                document.error = error
            if chunks_count is not None:
                document.chunks_count = chunks_count
            self.db.commit()
            self.db.refresh(document)
        return document

    def list_documents_by_knowledge_source(self, knowledge_source_id: UUID) -> List[DocumentEntity]:
        """Get all documents for a knowledge source"""
        return self.db.query(DocumentEntity).filter(
            DocumentEntity.knowledge_source_id == knowledge_source_id
        ).all()