from pydantic import Field, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict
from sentra_shared.core.logging import get_logger
logger = get_logger(__name__)

class SentraSettings(BaseSettings):
    llama_server_url: str = Field(default="http://localhost:11434", json_schema_extra={"env": "LLAMA_SERVER_URL"})
    knowledge_mount_path: str = Field(default="/mnt/sentra_knowledge", json_schema_extra={"env": "KNOWLEDGE_MOUNT_PATH"})

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="allow"
    )


try: # Validate settings on import
    settings = SentraSettings()
except ValidationError as e:
    error_details = "; ".join([f"{err['loc'][0]}: {err['msg']}" for err in e.errors()])
    logger.error(f"Configuration error: {error_details}")
    raise