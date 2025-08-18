import httpx
from fastmcp import FastMCP
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger("web_tool")

DDG_SEARCH_URL = "https://html.duckduckgo.com/html"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; SentraBot/1.0; +https://sentrabrain.com)",
    "Accept-Language": "en-US,en;q=0.9"
}


def register_web_tools(mcp: FastMCP):
    @mcp.tool(
        name="web.search",
        description="Perform a real-time internet search using DuckDuckGo.",
        
        title="Web Search",
    )
    async def web_search(query: str, top_k: int = 5, recency_days: int = 60) -> list[dict]:
        """Perform search via DuckDuckGo and return top_k results."""
        try:
            async with httpx.AsyncClient(timeout=10.0, headers=HEADERS) as client:
                resp = await client.post(DDG_SEARCH_URL, data={"q": query})
                if resp.status_code != 200:
                    return [{"error": f"Search failed with status {resp.status_code}"}]

                soup = BeautifulSoup(resp.text, "html.parser")
                results = []

                for result in soup.select("div.result.results_links_deep")[:top_k]:
                    title_el = result.select_one("a.result__a")
                    snippet_el = result.select_one("a.result__snippet") or result.select_one(".result__snippet")

                    if not title_el:
                        continue

                    title = title_el.get_text(strip=True)
                    url = title_el.get("href") or ""
                    if not url:
                        continue
                    snippet = snippet_el.get_text(strip=True) if snippet_el else ""

                    results.append({
                        "title": title,
                        "url": url,
                        "snippet": snippet
                    })

                return results

        except Exception as e:
            logger.warning(f"Search error: {e}")
            return [{"error": "Search failed"}]
