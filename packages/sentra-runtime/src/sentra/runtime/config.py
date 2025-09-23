"""Configuration settings for the Sentra engine."""
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Minimal configuration used by the engine."""

    use_dummy: bool = Field(
        default=False,
        json_schema_extra={"env": "USE_DUMMY"},
    )

    tool_allowlist: dict[str, list[str]] = Field(
        default_factory=lambda: {
            "sentra_agent": ["RagTool", "DbQueryTool"],
            "LegalDraftingAgent": ["RagTool"],
            "ListingsSearchAgent": ["DbQueryTool"],
        },
        json_schema_extra={"env": "AGENT_TOOL_ALLOWLIST"},
    )

    rag_source_allowlist: dict[str, list[str]] = Field(
        default_factory=lambda: {
            "sentra_agent": ["*"],
            "LegalDraftingAgent": ["legal-templates", "clauses"],
            "ListingsSearchAgent": ["re-listings"],
        },
        json_schema_extra={"env": "AGENT_SOURCE_ALLOWLIST"},
    )


settings = Settings()
