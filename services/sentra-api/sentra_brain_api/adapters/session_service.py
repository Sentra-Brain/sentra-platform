"""Singleton ADK SessionService for the API layer.

This uses the in-memory implementation which is suitable for development and
stateless container instances where cross-instance session persistence is not
required yet. A future enhancement will introduce a persistent implementation
(e.g. backed by Mongo or SQL) once durability across restarts is needed.

The service is intentionally lightweight and imported by request handlers.
"""
from __future__ import annotations

from typing import Optional
from google.adk.sessions import InMemorySessionService, Session  # type: ignore

APP_NAME = "sentra"  # Consistent app name for ADK session partitioning

_session_service: Optional[InMemorySessionService] = None


def get_session_service() -> InMemorySessionService:
    global _session_service
    if _session_service is None:
        _session_service = InMemorySessionService()
    return _session_service

__all__ = ["get_session_service", "APP_NAME", "Session"]
