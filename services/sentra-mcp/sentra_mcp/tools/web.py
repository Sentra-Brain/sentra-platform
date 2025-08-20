# sentra_mcp/tools/web.py
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Annotated, Any, List, Optional
from urllib.parse import urlparse, parse_qs, unquote

import httpx
from bs4 import BeautifulSoup
from bs4.element import Tag  # <-- for precise typing
from fastmcp import FastMCP
from pydantic import BaseModel, Field

logger = logging.getLogger("sentra_mcp.web_tool")

DDG_SEARCH_URL = "https://html.duckduckgo.com/html"

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; SentraBot/1.0; +https://sentrabrain.com)",
    "Accept-Language": "en-US,en;q=0.9",
}

# ---------- Output models ----------

class SearchResult(BaseModel):
    rank: int = Field(..., ge=1, description="1-based rank of the result")
    title: str
    url: str
    snippet: str = ""
    source: str = "duckduckgo_html"  # default, but we’ll also set it explicitly

class SearchResponse(BaseModel):
    query: str
    top_k: int
    fetched_at: datetime
    results: List[SearchResult]

# ---------- Helpers ----------

def _decode_ddg_redirect(href: str) -> str:
    """
    DuckDuckGo sometimes wraps links as /l/?uddg=<url-encoded-target>.
    """
    try:
        parsed = urlparse(href)
        qs = parse_qs(parsed.query)
        if "uddg" in qs and qs["uddg"]:
            return unquote(qs["uddg"][0])
        return href
    except Exception:
        return href

def _as_str_href(val: Any) -> Optional[str]:
    """
    Normalize a BeautifulSoup attribute value to a string href or None.
    It may be str | list[str] | None | other bs4 types.
    """
    if val is None:
        return None
    if isinstance(val, str):
        return val
    if isinstance(val, (list, tuple)):
        for item in val:
            if isinstance(item, str):
                return item
        return None
    return None

def _text(el: Any) -> str:
    try:
        return el.get_text(strip=True) if isinstance(el, Tag) else ""
    except Exception:
        return ""

# ---------- Tool registration ----------

def register_web_tools(mcp: FastMCP):
    @mcp.tool(
        name="web.search",
        title="Web Search",
        description="Perform a lightweight web search via DuckDuckGo HTML. Returns ranked results.",
    )
    async def web_search(
        query: Annotated[str, Field(min_length=2, max_length=256, description="Search query string")],
        top_k: Annotated[int, Field(ge=1, le=10, description="Number of results to return")] = 5,
        recency_days: Annotated[int, Field(ge=1, le=365, description="Freshness preference (best-effort)")]=60,
        lang: Annotated[str, Field(pattern=r"^[a-z]{2}(?:-[A-Z]{2})?$")] = "en-US",
        safe: Annotated[bool, Field(description="Prefer safe results if supported")] = True,
    ) -> SearchResponse:
        headers = dict(DEFAULT_HEADERS)
        headers["Accept-Language"] = f"{lang},{DEFAULT_HEADERS['Accept-Language']}"

        timeout = httpx.Timeout(connect=5.0, read=10.0, write=5.0, pool=5.0)
        limits = httpx.Limits(max_connections=50, max_keepalive_connections=20)

        try:
            async with httpx.AsyncClient(
                timeout=timeout,
                limits=limits,
                headers=headers,
                follow_redirects=True,
            ) as client:
                form = {"q": query}
                if safe:
                    form["kp"] = "1"  # best-effort safe search
                resp = await client.post(DDG_SEARCH_URL, data=form)

                if resp.status_code != 200:
                    logger.warning("DDG search failed: status=%s", resp.status_code)
                    return SearchResponse(
                        query=query,
                        top_k=top_k,
                        fetched_at=datetime.now(timezone.utc),
                        results=[],
                    )

                soup = BeautifulSoup(resp.text, "html.parser")
                # Select and filter only Tag instances (avoid NavigableString)
                blocks_raw = soup.select("div.result.results_links_deep") or soup.select("div.result")
                blocks: list[Tag] = [b for b in blocks_raw if isinstance(b, Tag)]

                results: list[SearchResult] = []
                for idx, block in enumerate(blocks, start=1):
                    if len(results) >= top_k:
                        break

                    a = block.select_one("a.result__a") or block.find("a", class_="result__a")
                    if not isinstance(a, Tag):
                        continue

                    href_val = _as_str_href(a.get("href"))
                    if not href_val:
                        continue
                    url = _decode_ddg_redirect(href_val)

                    title = _text(a)
                    if not title:
                        continue

                    snippet_el = block.select_one("a.result__snippet") or block.select_one(".result__snippet")
                    snippet = _text(snippet_el)

                    results.append(
                        SearchResult(
                            rank=idx,
                            title=title,
                            url=url,
                            snippet=snippet,
                            source="duckduckgo_html",  # explicit → silences Pylance “missing argument”
                        )
                    )

                return SearchResponse(
                    query=query,
                    top_k=top_k,
                    fetched_at=datetime.now(timezone.utc),
                    results=results,
                )

        except httpx.HTTPError as e:
            logger.warning("HTTP error performing search: %s", e)
            return SearchResponse(
                query=query,
                top_k=top_k,
                fetched_at=datetime.now(timezone.utc),
                results=[],
            )
        except Exception as e:
            logger.exception("Unexpected search error: %s", e)
            return SearchResponse(
                query=query,
                top_k=top_k,
                fetched_at=datetime.now(timezone.utc),
                results=[],
            )
