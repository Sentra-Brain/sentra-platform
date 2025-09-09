# packages/sentra-infra/src/sentra/infra/sql/repositories/document_repository_sql.py
from sqlalchemy.orm import Session
from sentra.domain.entities.document_entity import DocumentEntity
from sentra.domain.repository.document_repository import IDocumentRepository
from sentra.infra.sql.repositories.base_repository import BaseRepository
from uuid import UUID
from typing import Optional

class DocumentRepositorySql(BaseRepository[DocumentEntity], IDocumentRepository):
    def __init__(self, db: Session):
        super().__init__(DocumentEntity, db)

    def list_by_source(self, knowledge_source_id: Optional[UUID] = None, limit: int = 100, offset: int = 0) -> list[DocumentEntity]:
        query = self.db.query(self.model).filter(self.model.deleted_at.is_(None))
        if knowledge_source_id:
            query = query.filter(self.model.knowledge_source_id == knowledge_source_id)
        return query.offset(offset).limit(limit).all()

    def count_by_source(self, knowledge_source_id: Optional[UUID] = None) -> int:
        query = self.db.query(self.model).filter(self.model.deleted_at.is_(None))
        if knowledge_source_id:
            query = query.filter(self.model.knowledge_source_id == knowledge_source_id)
        return query.count()

    def update_status(self, document_id: UUID, status, error: Optional[str] = None, status_message: Optional[str] = None, chunks_count: Optional[int] = None) -> Optional[DocumentEntity]:
        document = self.get(document_id)
        if not document:
            return None
        document.status = status
        document.error = error
        document.status_message = status_message
        document.chunks_count = chunks_count
        return self.update(document)

    def list_by_user_or_source(self, user_id: UUID, knowledge_source_id: Optional[UUID] = None, limit: int = 100, offset: int = 0) -> list[DocumentEntity]:
        query = self.db.query(self.model).filter(
            self.model.created_by_id == user_id,
            self.model.deleted_at.is_(None)
        )
        if knowledge_source_id:
            query = query.filter(self.model.knowledge_source_id == knowledge_source_id)
        return query.offset(offset).limit(limit).all()

    def count_by_user_or_source(self, user_id: UUID, knowledge_source_id: Optional[UUID] = None) -> int:
        query = self.db.query(self.model).filter(
            self.model.created_by_id == user_id,
            self.model.deleted_at.is_(None)
        )
        if knowledge_source_id:
            query = query.filter(self.model.knowledge_source_id == knowledge_source_id)
        return query.count()

    def update_markdown_info(self, document_id: UUID, path: str, size: int, sha256: str) -> None:
        document = self.db.query(DocumentEntity).filter(DocumentEntity.id == document_id).first()
        if not document:
            raise ValueError(f"Document {document_id} not found")
        document.markdown_path = path
        document.markdown_bytes = size
        document.markdown_hash = sha256
        document.has_markdown = True
        self.db.commit()
