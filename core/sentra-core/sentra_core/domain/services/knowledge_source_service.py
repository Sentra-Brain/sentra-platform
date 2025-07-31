# sentra_core/domain/services/knowledge_source_service.py
from pathlib import Path
from uuid import UUID
from sentra_core.domain.entities.knowledge_source_entity import KnowledgeSourceEntity, KnowledgeSourceType
from sentra_core.domain.enums.knowledge import KnowledgeSourceStatus
from sentra_core.domain.repository.knowledge_source_repository import KnowledgeSourceRepository

class KnowledgeSourceService:
    def __init__(self, repository: KnowledgeSourceRepository, mount_path: str):
        self.repository = repository
        self.mount_path = Path(mount_path)

    def create_knowledge_source(self, source: KnowledgeSourceEntity) -> KnowledgeSourceEntity:
        if source.type == KnowledgeSourceType.FOLDER:
            if not source.path:
                raise ValueError("Path is required for folder-type knowledge sources.")
            self._validate_path(source.path)
        return self.repository.create(source)

    def update_status(self, source_id: UUID, enabled: bool) -> KnowledgeSourceEntity:
        source = self.repository.get(source_id)
        if not source:
            raise ValueError("Knowledge source not found.")
        source.status = KnowledgeSourceStatus.ACTIVE if enabled else KnowledgeSourceStatus.DISABLED
        return self.repository.update(source)

    def _validate_path(self, raw_path: str) -> None:
        requested = Path(raw_path).resolve()
        if not requested.is_relative_to(self.mount_path.resolve()):
            raise ValueError(f"Path must be under {self.mount_path}")
