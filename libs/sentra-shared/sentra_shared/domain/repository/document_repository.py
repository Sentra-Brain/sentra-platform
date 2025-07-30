from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sentra_shared.domain.entities.document_entity import DocumentEntity
from sentra_shared.domain.repository.base_repository import BaseRepository


class DocumentRepository(BaseRepository[DocumentEntity]):
    def __init__(self, db: Session):
        super().__init__(DocumentEntity, db)

    def list_by_source(
        self,
        knowledge_source_id: Optional[UUID] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[DocumentEntity]:
        query = self.db.query(self.model).filter(self.model.deleted_at.is_(None))
        if knowledge_source_id:
            query = query.filter(self.model.knowledge_source_id == knowledge_source_id)
        return query.offset(offset).limit(limit).all()

    def count_by_source(
        self,
        knowledge_source_id: Optional[UUID] = None
    ) -> int:
        query = self.db.query(self.model).filter(self.model.deleted_at.is_(None))
        if knowledge_source_id:
            query = query.filter(self.model.knowledge_source_id == knowledge_source_id)
        return query.count()

    def update_status(
        self,
        document_id: UUID,
        status,
        error: Optional[str] = None,
        status_message: Optional[str] = None,
        chunks_count: Optional[int] = None
    ) -> Optional[DocumentEntity]:
        document = self.get(document_id)
        if not document:
            return None
        document.status = status
        document.error = error
        document.status_message = status_message
        document.chunks_count = chunks_count
        return self.update(document)
