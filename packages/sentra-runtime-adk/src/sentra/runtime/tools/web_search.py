from __future__ import annotations
from typing import List, TypedDict
import asyncio
from ddgs import DDGS

class SearchItem(TypedDict):
    title: str
    url: str
    snippet: str

def _coerce_top_k(value, default: int = 5, lo: int = 1, hi: int = 8) -> int:
    try:
        iv = int(value)
    except Exception:
        iv = default
    if iv < lo: iv = lo
    if iv > hi: iv = hi
    return iv

def _ddgs_text_sync(query: str, max_results: int):
    # DDGS is synchronous; use a context manager for proper session reuse
    with DDGS() as ddgs:
        # backend="html" is stable; you can switch to "lite" if needed
        return list(ddgs.text(
            query,
            max_results=max_results,
            region="wt-wt",       # world-wide, neutral
            safesearch="moderate",# 'off'|'moderate'|'strict'
            backend="html",       # 'html'|'lite'
            timelimit=None,       # e.g. 'd','w','m','y'
        ))

async def web_search(query: str, top_k: int = 5) -> dict:
    """
    Web Search via ddgs (DDGS | Dux Distributed Global Search).
    Returns: {"status":"success","results":[{title,url,snippet}...]} | {"status":"error",...}
    """
    if not isinstance(query, str) or not query.strip():
        return {"status": "error", "error": "Empty query"}

    k = _coerce_top_k(top_k, default=5, lo=1, hi=8)

    try:
        # Run the blocking DDGS search off the event loop
        rows = await asyncio.to_thread(_ddgs_text_sync, query, k)

        # Map ddgs fields -> Our schema
        results: List[SearchItem] = []
        for r in rows[:k]:
            title = (r.get("title") or "").strip()
            url = (r.get("href") or "").strip()
            snippet = (r.get("body") or "").strip()
            if not (title and url and url.startswith("http")):
                continue
            results.append({
                "title": title[:300],
                "url": url,
                "snippet": snippet[:500],
            })

        return {"status": "success", "results": results}

    except Exception as e:
        # preserve error contract
        return {"status": "error", "error": f"Search error: {e}"}
