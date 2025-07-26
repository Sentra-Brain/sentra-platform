from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, ValidationError
from sentra_shared.core.logging import get_logger


logger = get_logger(__name__)

class PostgresSettings(BaseSettings):
    database_url: str = Field(..., json_schema_extra={"env": "DATABASE_URL"})
    initial_admin_username: str = Field(..., json_schema_extra={"env": "INITIAL_ADMIN_USERNAME"})
    initial_admin_email: str = Field(..., json_schema_extra={"env": "INITIAL_ADMIN_EMAIL"})
    initial_admin_password: str = Field(..., json_schema_extra={"env": "INITIAL_ADMIN_PASSWORD"})
    secret_key: str = Field(..., json_schema_extra={"env": "SECRET_KEY"})
    algorithm: str = Field(..., json_schema_extra={"env": "ALGORITHM"})
    access_token_expire_minutes: int = Field(..., json_schema_extra={"env": "ACCESS_TOKEN_EXPIRE_MINUTES"})

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="allow"
    )

try: # Validate settings on import
    settings = PostgresSettings()
except ValidationError as e:
    error_details = "; ".join([f"{err['loc'][0]}: {err['msg']}" for err in e.errors()])
    logger.error(f"Configuration error: {error_details}")
    raise
