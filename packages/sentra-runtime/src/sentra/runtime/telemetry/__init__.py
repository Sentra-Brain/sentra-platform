"""Telemetry utilities for logging and metrics.

This module exposes lightweight helpers used across the engine to emit
structured logs.  The intention is to provide a single place to enrich
events before they are written so future metrics backends or tracing
systems can hook in without touching the call‑sites.
"""

from __future__ import annotations

import logging
from uuid import uuid4

from sentra.schemas import Event


logger = logging.getLogger(__name__)


def emit_event_log(event: Event) -> None:
    """Emit a structured log for ``event``.

    A ``task_run_id`` is injected when missing to aid in correlating events
    that belong to the same conversation.  Only non-``None`` values are
    included in the final log record.
    """

    if event.task_run_id is None:
        event.task_run_id = uuid4().hex
    logger.info("event", extra=event.model_dump(exclude_none=True))


__all__ = ["emit_event_log"]

