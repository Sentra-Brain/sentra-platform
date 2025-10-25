"""Telemetry utilities for logging and metrics.

This module exposes lightweight helpers used across the engine to emit
structured logs.  The intention is to provide a single place to enrich
events before they are written so future metrics backends or tracing
systems can hook in without touching the call‑sites.
"""

from __future__ import annotations

import logging
from google.adk.events.event import Event


logger = logging.getLogger(__name__)


def emit_event_log(event: Event) -> None:
    """Emit a structured log for an ADK Event."""
    try:
        flat = event.model_dump(exclude_none=True)  # type: ignore[attr-defined]
    except Exception:
        # Fallback for lightweight test stubs
        flat = {
            "author": getattr(event, "author", None),
        }
    md = getattr(event, "custom_metadata", {}) or {}
    for k, v in md.items():
        flat.setdefault(k, v)
    logger.info("event", extra=flat)


__all__ = ["emit_event_log"]

