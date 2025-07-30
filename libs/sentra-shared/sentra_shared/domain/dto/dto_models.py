# sentra_shared/dto/dto_models.py

from uuid import UUID
from datetime import datetime
from sentra_shared.domain.enums.document import DocumentFileType, DocumentStatus
from sentra_shared.domain.enums.knowledge import (
    KnowledgeSourceType,
    KnowledgeSourceVisibility,
    KnowledgeSourceStatus,
)

# DTO for UserEntity
class UserDTO:
    def __init__(
        self,
        id: UUID,
        username: str,
        email: str,
        full_name: str,
        disabled: bool,
        roles: list[str],
        created_at: datetime,
        updated_at: datetime | None
    ):
        self.id = id
        self.username = username
        self.email = email
        self.full_name = full_name
        self.disabled = disabled
        self.roles = roles
        self.created_at = created_at
        self.updated_at = updated_at


# DTO for ConversationEntity
class ConversationDTO:
    def __init__(
        self,
        id: UUID,
        title: str | None,
        description: str | None,
        initial_prompt: str | None,
        created_by_id: UUID,
        created_at: datetime,
        updated_at: datetime | None
    ):
        self.id = id
        self.title = title
        self.description = description
        self.initial_prompt = initial_prompt
        self.created_by_id = created_by_id
        self.created_at = created_at
        self.updated_at = updated_at


# DTO for DocumentEntity
class DocumentDTO:
    def __init__(
        self,
        id: UUID,
        filename: str,
        display_name: str,
        description: str | None,
        filetype: DocumentFileType,
        path: str,
        status: DocumentStatus,
        status_message: str | None,
        error: str | None,
        chunks_count: int | None,
        knowledge_source_id: UUID,
        created_by_id: UUID,
        created_at: datetime,
        updated_at: datetime | None
    ):
        self.id = id
        self.filename = filename
        self.display_name = display_name
        self.description = description
        self.filetype = filetype
        self.path = path
        self.status = status
        self.status_message = status_message
        self.error = error
        self.chunks_count = chunks_count
        self.knowledge_source_id = knowledge_source_id
        self.created_by_id = created_by_id
        self.created_at = created_at
        self.updated_at = updated_at


# DTO for KnowledgeSourceEntity
class KnowledgeSourceDTO:
    def __init__(
        self,
        id: UUID,
        name: str,
        type: KnowledgeSourceType,
        path: str | None,
        description: str | None,
        visibility: KnowledgeSourceVisibility,
        auto_index: bool,
        status: KnowledgeSourceStatus,
        created_by_id: UUID,
        created_at: datetime,
        updated_at: datetime | None
    ):
        self.id = id
        self.name = name
        self.type = type
        self.path = path
        self.description = description
        self.visibility = visibility
        self.auto_index = auto_index
        self.status = status
        self.created_by_id = created_by_id
        self.created_at = created_at
        self.updated_at = updated_at


# DTO for SystemSettings
class SystemSettingsDTO:
    def __init__(
        self,
        id: UUID,
        workspace_name: str,
        license_type: str,
        maintenance_mode: bool,
        default_language: str,
        log_retention_days: int,
        max_users: int,
        created_at: datetime,
        updated_at: datetime | None
    ):
        self.id = id
        self.workspace_name = workspace_name
        self.license_type = license_type
        self.maintenance_mode = maintenance_mode
        self.default_language = default_language
        self.log_retention_days = log_retention_days
        self.max_users = max_users
        self.created_at = created_at
        self.updated_at = updated_at
