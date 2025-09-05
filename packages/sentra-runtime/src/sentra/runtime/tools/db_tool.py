"""Stubbed database query tool."""
from __future__ import annotations

import logging

from sentra.runtime.policies import retry_with_backoff


logger = logging.getLogger(__name__)


class DbQueryTool:
    """Read-only helper that will query the core database."""

    async def _fetch_property_summaries(self, limit: int) -> str:
        logger.info("Stubbed DB query for %s property summaries", limit)
        # TODO: integrate with sentra_core repositories
        return "TODO: property summaries"

    async def get_property_summaries(self, limit: int = 3) -> str:
        """Return mocked property summaries."""

        result = await retry_with_backoff(
            lambda: self._fetch_property_summaries(limit),
            logger=logger,
            label="db.get_property_summaries",
        )
        return result or ""

    async def _fetch_listings(self, city: str, max_budget: float) -> list[str]:
        logger.debug(
            "Stubbed DB query for listings in %s with budget %.2f", city, max_budget
        )
        listings = [
            f"Flat in {city}, 85 m², €950/mo",
            "Loft in Salamanca, 60 m², €890/mo",
            "Studio in Seville, 45 m², €700/mo",
        ]
        logger.info("Returning %d mocked listings", len(listings[:3]))
        return listings[:3]

    async def get_listings(self, city: str, max_budget: float) -> list[str]:
        """Return a small list of mocked listings."""

        listings = await retry_with_backoff(
            lambda: self._fetch_listings(city, max_budget),
            logger=logger,
            label="db.get_listings",
        )
        return listings or []
