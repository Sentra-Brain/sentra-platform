"""Process-wide ADK memory service singleton.

This wraps the ADK ``InMemoryMemoryService`` and provides helper functions
used by the runtime (context building) and API layer (session indexing).

For now we keep an *in‑process* set of already-indexed session IDs to avoid
adding the same session multiple times. When a persistent memory backend is
introduced this module can evolve without changing call sites.
"""
from __future__ import annotations

from typing import Iterable, Any

try:  # pragma: no cover - exercised implicitly in integration paths
    from google.adk.memory import InMemoryMemoryService  # type: ignore
except Exception:  # pragma: no cover - tests provide a stub
    InMemoryMemoryService = None  # type: ignore

APP_NAME = "sentra"

_indexed_sessions: set[str] = set()
_memory_service: InMemoryMemoryService | None = None  # type: ignore[name-defined]


def get_memory_service() -> Any:  # return type kept loose to tolerate test stubs
    global _memory_service
    if _memory_service is None:
        if InMemoryMemoryService is None:  # test environment w/out real lib
            raise RuntimeError("InMemoryMemoryService not available (stub not installed)")
        _memory_service = InMemoryMemoryService()  # type: ignore[call-arg]
    return _memory_service


async def add_session_to_memory(session: Any) -> None:
    """Index a session's events into long‑term memory if not already indexed.

    A session is only indexed once; further calls are ignored to prevent
    duplicate memory inflation when multiple ``message_final`` events stream
    over time for the same logical session.
    """
    sid = getattr(session, "id", None)
    if not sid or sid in _indexed_sessions:
        return
    svc = get_memory_service()
    try:
        await svc.add_session_to_memory(session)  # type: ignore[attr-defined]
        _indexed_sessions.add(sid)
    except Exception:  # pragma: no cover - defensive
        # Silent failure keeps conversation flow resilient; logging performed by callers if needed.
        return


async def search_memories(user_id: str, query: str, limit: int = 5) -> list[Any]:
    """Search memory for ``user_id`` returning a list of result objects.

    Each result is expected to expose ``text``. We intentionally do *not*
    normalise shape here so that upstream code can flexibly adapt once a
    richer backend is introduced.
    """
    svc = get_memory_service()
    try:
        return await svc.search_memory(app_name=APP_NAME, user_id=user_id, query=query, limit=limit)  # type: ignore[attr-defined]
    except Exception:  # pragma: no cover - defensive
        return []


__all__ = [
    "APP_NAME",
    "get_memory_service",
    "add_session_to_memory",
    "search_memories",
]
