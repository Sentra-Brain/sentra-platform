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

    async def get_listings(self, city: str, max_budget: float) -> list[str]:
        """Return a small list of mocked listings.

        This placeholder implementation simply returns deterministic
        examples so that agents can be exercised without a database
        connection.
        """

        logger.debug(
            "Stubbed DB query for listings in %s with budget %.2f",
            city,
            max_budget,
        )
        listings = [
            f"Flat in {city}, 85 m², €950/mo",
            "Loft in Salamanca, 60 m², €890/mo",
            "Studio in Seville, 45 m², €700/mo",
        ]
        logger.info("Returning %d mocked listings", len(listings[:3]))
        return listings[:3]
