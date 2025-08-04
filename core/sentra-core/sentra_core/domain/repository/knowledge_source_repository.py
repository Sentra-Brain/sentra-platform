from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sentra_core.domain.entities.knowledge_source_entity import KnowledgeSourceEntity
from sentra_core.domain.enums.knowledge import KnowledgeSourceType, KnowledgeSourceStatus
from sentra_core.domain.repository.base_repository import BaseRepository


class KnowledgeSourceRepository(BaseRepository[KnowledgeSourceEntity]):
    def __init__(self, db: Session):
        super().__init__(KnowledgeSourceEntity, db)

    def list_by_user(self, created_by: UUID, limit: int = 100, offset: int = 0) -> List[KnowledgeSourceEntity]:
        return self.filter_by(created_by_id=created_by, limit=limit, offset=offset)

    def count_by_user(self, created_by: UUID) -> int:
        return self.db.query(self.model).filter(
            self.model.created_by_id == created_by,
            self.model.deleted_at.is_(None)
        ).count()

    def get_folder_sources(self, auto_index_only: bool = True) -> List[KnowledgeSourceEntity]:
        query = self.db.query(self.model).filter(
            self.model.type == KnowledgeSourceType.FOLDER,
            self.model.status == KnowledgeSourceStatus.ACTIVE,
            self.model.deleted_at.is_(None)
        )
        if auto_index_only:
            query = query.filter(self.model.auto_index == True)
        return query.all()
    
