"""Test shim for `google.adk.sessions`.

This module provides a minimal `DatabaseSessionService` symbol so that
imports in production modules succeed at test collection time. The real
implementation lives elsewhere; this shim is only for unit tests and
should not replace real dependencies in production.
"""

from typing import Any


class DatabaseSessionService:  # pragma: no cover - test shim
    """Minimal stand-in for the real DatabaseSessionService.

    Only implements the minimal interface required by import-time
    references in the test suite. Tests expecting behaviour should
    patch or inject a proper mock.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._started = False

    def start(self) -> None:
        self._started = True

    def stop(self) -> None:
        self._started = False

    @property
    def started(self) -> bool:
        return self._started


__all__ = ["DatabaseSessionService"]
