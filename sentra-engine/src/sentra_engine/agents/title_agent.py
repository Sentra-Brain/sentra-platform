from __future__ import annotations

"""Agent responsible for generating session titles."""

import logging
import re
from typing import Sequence

logger = logging.getLogger(__name__)


class TitleAgent:
    """Generate short descriptive titles for sessions.

    This agent provides a lightweight heuristic-based title generation
    that can later be extended to call an LLM. It keeps titles under
    50 characters and uses a simple word clipping strategy.
    """

    async def generate(self, messages: Sequence[str]) -> str:
        """Generate a title from a sequence of message contents.

        Args:
            messages: A sequence of message strings, typically the first
                user message and the assistant response.

        Returns:
            A cleaned and trimmed title string.
        """

        combined = " ".join(m or "" for m in messages).strip()
        return self._generate_title_heuristic(combined)

    def generate_initial(self, initial_prompt: str) -> str:
        """Generate a quick title from the initial prompt."""
        return self._generate_title_heuristic(initial_prompt)

    # ------------------------------------------------------------------
    def _generate_title_heuristic(self, text: str) -> str:
        words = re.findall(r"\w+(?:['-]\w+)?|[?]", text)[:6]
        title = " ".join(words)
        if text.strip().endswith("?") and not title.endswith("?"):
            title += "?"
        return self._clean_title(title)

    def _clean_title(self, title: str) -> str:
        title = re.sub(r'^\"|\"$|^\'|\'$|^`|`$', '', title.strip())
        if len(title) > 50:
            title = title[:47] + "..."
        return title.strip() or "New Session"
