import enum
from sqlalchemy import Column, String, Boolean, ForeignKey, Enum, Text
from sqlalchemy.dialects.postgresql import UUID
from .base_entity import BaseEntity


class KnowledgeSourceType(enum.Enum):
    UPLOAD = "upload"
    FOLDER = "folder"
    EXTERNAL_API = "external_api"
    MANUAL = "manual"
    MCP_TOOL = "mcp_tool"


class KnowledgeSourceVisibility(enum.Enum):
    PRIVATE = "private"
    SHARED = "shared"
    ORG_WIDE = "org-wide"


class KnowledgeSourceStatus(enum.Enum):
    ACTIVE = "active"
    DISABLED = "disabled"
    ERROR = "error"


class KnowledgeSourceEntity(BaseEntity):
    __tablename__ = "knowledge_sources"

    name = Column(Text, nullable=False)
    type = Column(Enum(KnowledgeSourceType), nullable=False)
    path = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    visibility = Column(Enum(KnowledgeSourceVisibility), nullable=False, default=KnowledgeSourceVisibility.PRIVATE)
    auto_index = Column(Boolean, nullable=False, default=False)
    status = Column(Enum(KnowledgeSourceStatus), nullable=False, default=KnowledgeSourceStatus.ACTIVE)