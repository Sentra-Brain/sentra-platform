from typing import Optional
from google.adk.sessions import DatabaseSessionService, Session
from sentra.shared.settings import settings

APP_NAME = "sentra"

_session_service: Optional[DatabaseSessionService] = None

def get_adk_session_service() -> DatabaseSessionService:
    global _session_service
    if _session_service is None:
        db_url = settings.database_url
        if not db_url:
            raise RuntimeError("settings.database_url must be set for DatabaseSessionService.")
        _session_service = DatabaseSessionService(db_url=db_url, app_name=APP_NAME)
    return _session_service

__all__ = ["get_adk_session_service", "APP_NAME", "Session"]
