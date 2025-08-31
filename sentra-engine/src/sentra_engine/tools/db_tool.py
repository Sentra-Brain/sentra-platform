"""Stubbed database query tool."""
from __future__ import annotations

import logging


logger = logging.getLogger(__name__)


class DbQueryTool:
    """Read-only helper that will query the core database."""

    def get_property_summaries(self, limit: int = 3) -> str:
        """Return mocked property summaries.

        In the future this will query the SQLAlchemy repositories from
        ``sentra_core``.
        """

        logger.info("Stubbed DB query for %s property summaries", limit)
        # TODO: integrate with sentra_core repositories
        return "TODO: property summaries"
