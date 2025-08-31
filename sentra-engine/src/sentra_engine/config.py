"""Configuration settings for the Sentra engine."""
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Minimal configuration used by the engine."""

    use_dummy: bool = Field(
        default=False,
        json_schema_extra={"env": "USE_DUMMY"},
    )


settings = Settings()
