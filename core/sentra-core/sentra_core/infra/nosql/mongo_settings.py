# sentra-core/sentra_core/infra/nosql/mongo_settings.py
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, ValidationError
from sentra_core.logging import get_logger


logger = get_logger(__name__)

class MongoSettings(BaseSettings):
    mongo_user: str = Field(default="", json_schema_extra={"env": "MONGO_USERNAME"})
    mongo_password: str = Field(default="", json_schema_extra={"env": "MONGO_PASSWORD"})
    mongo_host: str = Field(default="localhost", json_schema_extra={"env": "MONGO_HOST"})
    mongo_port: int = Field(default=27017, json_schema_extra={"env": "MONGO_PORT"})
    mongo_database: str = Field(default="sentra_brain", json_schema_extra={"env": "MONGO_DATABASE"})
    mongo_url: str = Field(default="", json_schema_extra={"env": "MONGO_URL"})

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="allow"
    )

try: # Validate settings on import
    settings = MongoSettings()
except ValidationError as e:
    error_details = "; ".join([f"{err['loc'][0]}: {err['msg']}" for err in e.errors()])
    logger.error(f"Configuration error: {error_details}")
    raise
