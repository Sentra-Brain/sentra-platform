# sentra_brain_api/features/knowledge/repository.py

from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sentra_brain_api.domain.knowledge_source_entity import KnowledgeSourceEntity
from sentra_brain_api.domain.document_entity import DocumentEntity


class KnowledgeRepository:
    def __init__(self, db: Session):
        self.db = db

    # Knowledge Source methods
    def create_knowledge_source(self, knowledge_source: KnowledgeSourceEntity) -> KnowledgeSourceEntity:
        self.db.add(knowledge_source)
        self.db.commit()
        self.db.refresh(knowledge_source)
        return knowledge_source

    def get_knowledge_source_by_id(self, source_id: UUID) -> Optional[KnowledgeSourceEntity]:
        return self.db.query(KnowledgeSourceEntity).filter(KnowledgeSourceEntity.id == source_id).first()

    def list_knowledge_sources(self, created_by: Optional[UUID] = None, limit: int = 100, offset: int = 0) -> List[KnowledgeSourceEntity]:
        query = self.db.query(KnowledgeSourceEntity)
        if created_by:
            query = query.filter(KnowledgeSourceEntity.created_by == created_by)
        return query.offset(offset).limit(limit).all()

    def get_knowledge_sources_count(self, created_by: Optional[UUID] = None) -> int:
        query = self.db.query(KnowledgeSourceEntity)
        if created_by:
            query = query.filter(KnowledgeSourceEntity.created_by == created_by)
        return query.count()

    def get_folder_knowledge_sources(self, auto_index_only: bool = True) -> List[KnowledgeSourceEntity]:
        """Get folder-type knowledge sources for scanning"""
        from sentra_brain_api.domain.knowledge_source_entity import KnowledgeSourceType, KnowledgeSourceStatus
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

    def list_documents(self, uploaded_by: Optional[UUID] = None, knowledge_source_id: Optional[UUID] = None, 
                      limit: int = 100, offset: int = 0) -> List[DocumentEntity]:
        query = self.db.query(DocumentEntity)
        if uploaded_by:
            query = query.filter(DocumentEntity.uploaded_by == uploaded_by)
        if knowledge_source_id:
            query = query.filter(DocumentEntity.knowledge_source_id == knowledge_source_id)
        return query.offset(offset).limit(limit).all()

    def get_documents_count(self, uploaded_by: Optional[UUID] = None, knowledge_source_id: Optional[UUID] = None) -> int:
        query = self.db.query(DocumentEntity)
        if uploaded_by:
            query = query.filter(DocumentEntity.uploaded_by == uploaded_by)
        if knowledge_source_id:
            query = query.filter(DocumentEntity.knowledge_source_id == knowledge_source_id)
        return query.count()

    def update_document_status(self, document_id: UUID, status: str, error: Optional[str] = None, chunks_count: Optional[int] = None) -> Optional[DocumentEntity]:
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