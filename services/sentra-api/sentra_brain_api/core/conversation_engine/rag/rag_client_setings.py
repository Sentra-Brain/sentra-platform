# sentra_brain_api/core/conversation_engine/settings/rag_client_settings.py

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class RagClientSettings(BaseSettings):
    rag_server_url: str = Field(default="http://localhost:9100", json_schema_extra={"env": "RAG_SERVER_URL"})
    query_timeout: int = Field(default=10, json_schema_extra={"env": "RAG_QUERY_TIMEOUT"})

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="allow"
    )

settings = RagClientSettings()
