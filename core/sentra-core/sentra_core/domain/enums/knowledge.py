# sentra_core/domain/enums/knowledge.py
import enum

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
