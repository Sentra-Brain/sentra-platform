# services/sentra-mcp/sentra_mcp/tools/web.py
from __future__ import annotations

from sentra_core.logging import get_logger
from typing import Annotated, List, TypedDict
from pydantic import Field
import httpx
from bs4 import BeautifulSoup
from fastmcp import FastMCP

DDG_SEARCH_URL = "https://html.duckduckgo.com/html"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; SentraBot/1.0; +https://sentrabrain.com)",
    "Accept-Language": "en-US,en;q=0.9",
}

class SearchItem(TypedDict):
    title: str
    url: str
    snippet: str

logger = get_logger(__name__)


def register_web_tools(mcp: FastMCP) -> None:
    @mcp.tool(
        name="web.search.v1",
        title="Web Search",
        description="Search the web with DuckDuckGo HTML endpoint and return top results.",
    )
    async def web_search(
        query: Annotated[str, "Search query string"],
        top_k: Annotated[int, Field(description="Number of results", ge=1, le=8)] = 5,
    ) -> list[dict]:
        """
        Returns MCP content blocks:
        - text summary
        - json with {"results": [ {title, url, snippet}, ... ]}
        """
        logger.info("Web search for query: %s", query)
        results: List[SearchItem] = []
        try:
            async with httpx.AsyncClient(timeout=10.0, headers=HEADERS) as client:
                resp = await client.post(DDG_SEARCH_URL, data={"q": query})
                if resp.status_code != 200:
                    return [{"type": "text", "text": f"Search failed: HTTP {resp.status_code}"}]

                soup = BeautifulSoup(resp.text, "html.parser")
                cards = soup.select("div.result")  # tolerant selector

                for el in cards[:top_k]:
                    a = el.select_one("a.result__a")
                    if not a or not a.text:
                        continue
                    href = a.get("href") or ""
                    if not isinstance(href, str) or not href.startswith("http"):
                        continue
                    snippet_el = el.select_one(".result__snippet, a.result__snippet")
                    snippet = (snippet_el.get_text(" ", strip=True) if snippet_el else "")[:500]

                    results.append({
                        "title": a.get_text(" ", strip=True)[:300],
                        "url": href,
                        "snippet": snippet,
                    })

        except Exception as e:
            return [{"type": "text", "text": f"Search error: {e}"}]

        return [
            {"type": "text", "text": f"{len(results)} results for “{query}”"},
            {"type": "json", "json": {"results": results}},
        ]
