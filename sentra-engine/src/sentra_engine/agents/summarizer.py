from __future__ import annotations

"""Simple summarizer agent used to maintain rolling conversation memory."""

from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


async def update_summary_and_entities(
    conversation_id: str, new_messages: List[str]
) -> Tuple[str, Dict[str, List[str]]]:
    """Update summary and entity memory for a given conversation.

    This is a placeholder implementation that generates a very small summary and
    a fake entity map. A future version will call an LLM and persist the data
    to a database.

    Args:
        conversation_id: Identifier of the conversation being summarised.
        new_messages: Newly received messages that should be summarised.

    Returns:
        A tuple containing the updated summary string and a dictionary with
        extracted entities.
    """

    # Extremely small "summary" just joining the latest messages. In a real
    # implementation this would call an LLM or dedicated summarisation service.
    summary = " ".join(m.strip() for m in new_messages[-2:])

    # Fake entity extraction result. This keeps the shape expected by callers
    # without requiring NLP libraries.
    entities: Dict[str, List[str]] = {"persons": ["John"], "orgs": ["Acme Inc."]}

    # TODO: Replace with real summarisation logic and entity extraction.

    # Simulate saving to a database via sentra-core repository stub.
    logger.info("Persisted summary and entity map for %s", conversation_id)

    return summary, entities
