import os
from dotenv import load_dotenv
from pydantic import Field, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict
from sentra_brain_api.crosscutting.logging import get_logger


load_dotenv()

logger = get_logger(__name__)


class Settings(BaseSettings):

    # MongoDB
    mongo_user: str = Field(default="", env="MONGO_USERNAME")
    mongo_password: str = Field(default="", env="MONGO_PASSWORD")
    mongo_host: str = Field(default="localhost", env="MONGO_HOST")
    mongo_port: int = Field(default=27017, env="MONGO_PORT")
    mongo_database: str = Field(default="sentra_brain", env="MONGO_DATABASE")
    mongo_url: str = Field(default="", env="MONGO_URL")
    # PostgreSQL
    database_url: str = Field(..., env="DATABASE_URL")
    initial_admin_username: str = Field(..., env="INITIAL_ADMIN_USERNAME")
    initial_admin_email: str = Field(..., env="INITIAL_ADMIN_EMAIL")
    initial_admin_password: str = Field(..., env="INITIAL_ADMIN_PASSWORD")
    secret_key: str = Field(..., env="SECRET_KEY")
    algorithm: str = Field(..., env="ALGORITHM")
    access_token_expire_minutes: int = Field(..., env="ACCESS_TOKEN_EXPIRE_MINUTES")

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="allow"
    )

try: # Validate settings on import
    settings = Settings()
except ValidationError as e:
    logger.error(f"Configuration error: {e}")
    raise
