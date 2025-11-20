# """Singleton ADK SessionService for the API layer.

# This uses the in-memory implementation which is suitable for development and
# stateless container instances where cross-instance session persistence is not
# required yet. A future enhancement will introduce a persistent implementation
# (e.g. backed by Mongo or SQL) once durability across restarts is needed.

# The service is intentionally lightweight and imported by request handlers.
# """
# from __future__ import annotations

# from typing import Optional
# from google.adk.sessions import DatabaseSessionService, Session  # type: ignore

# APP_NAME = "sentra"  # Consistent app name for ADK session partitioning

# _session_service: Optional[DatabaseSessionService] = None


# import os

# def get_session_service() -> DatabaseSessionService:
#     global _session_service
#     if _session_service is None:
#         db_url = os.environ.get("POSTGRES_URL") or os.environ.get("DATABASE_URL")
#         if not db_url:
#             raise RuntimeError("POSTGRES_URL or DATABASE_URL environment variable must be set for DatabaseSessionService.")
#         _session_service = DatabaseSessionService(db_url=db_url, app_name=APP_NAME)
#     return _session_service

# __all__ = ["get_session_service", "APP_NAME", "Session"]
