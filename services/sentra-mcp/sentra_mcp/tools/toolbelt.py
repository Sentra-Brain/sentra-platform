from __future__ import annotations

import base64
import csv
import hashlib
import io
from json import tool
import os
import re
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from zoneinfo import ZoneInfo
from urllib.parse import urlparse
from fastmcp import FastMCP

import httpx



_FLAG_MAP = {
    "IGNORECASE": re.IGNORECASE,
    "I": re.IGNORECASE,
    "MULTILINE": re.MULTILINE,
    "M": re.MULTILINE,
    "DOTALL": re.DOTALL,
    "S": re.DOTALL,
}


def _regex_flags(flag_list: List[str]) -> int:
    flags = 0
    for name in flag_list:
        flags |= _FLAG_MAP.get(name.upper(), 0)
    return flags


def _http_allowlist() -> set[str]:
    raw = os.getenv("MCP_HTTP_ALLOWLIST", "")
    return {h.strip().lower() for h in raw.split(",") if h.strip()}


def _fs_root() -> Path:
    root = Path(os.getenv("MCP_FS_ROOT", ".")).resolve()
    return root


def _resolve_fs(path: str) -> Path:
    root = _fs_root()
    full = (root / path).resolve()
    if not str(full).startswith(str(root)):
        raise ValueError("Path outside of sandbox")
    return full

def register_toolbelt(mcp: FastMCP) -> None:
    @mcp.tool("echo")
    def echo(text: str) -> str:
        return text


    @mcp.tool("text.truncate")
    def text_truncate(text: str, max: int = 8192) -> str:  # noqa: A002
        return text[:max]


    @mcp.tool("text.extract")
    def text_extract(text: str, regex: str, flags: List[str] | None = None) -> List[str]:
        comp = re.compile(regex, _regex_flags(flags or []))
        return comp.findall(text)


    @mcp.tool("text.replace")
    def text_replace(
        text: str,
        regex: str,
        repl: str,
        count: int = 0,
        flags: List[str] | None = None,
    ) -> str:
        comp = re.compile(regex, _regex_flags(flags or []))
        return comp.sub(repl, text, count=count)


    @mcp.tool("uuid.new")
    def uuid_new() -> str:
        return str(uuid.uuid4())


    @mcp.tool("time.now")
    def time_now(fmt: str = "iso", tz: str = "UTC") -> str | int:
        try:
            zone = ZoneInfo(tz)
        except Exception:
            zone = ZoneInfo("UTC")
        now = datetime.now(zone)
        if fmt.lower() == "unix":
            return int(now.timestamp())
        return now.isoformat()


    @mcp.tool("sleep")
    def sleep_ms(ms: int) -> Dict[str, Any]:
        ms = max(0, min(ms, 5000))
        start = datetime.now(timezone.utc).isoformat() + "Z"
        time.sleep(ms / 1000)
        end = datetime.now(timezone.utc).isoformat() + "Z"
        return {"slept_ms": ms, "started": start, "ended": end}


    @mcp.tool("hash.sha256")
    def hash_sha256(text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()


    @mcp.tool("base64.encode")
    def b64_encode(text: str) -> str:
        return base64.b64encode(text.encode("utf-8")).decode("ascii")


    @mcp.tool("base64.decode")
    def b64_decode(b64: str) -> str:
        return base64.b64decode(b64.encode("ascii")).decode("utf-8")


    @mcp.tool("http.get")
    def http_get(url: str, timeout: int = 10, max: int = 8192) -> Dict[str, Any]:  # noqa: A002
        parsed = urlparse(url)
        host = (parsed.hostname or "").lower()
        if parsed.scheme not in {"http", "https"}:
            raise ValueError("Only HTTP/HTTPS URLs allowed")
        if host not in _http_allowlist():
            raise ValueError("Host not allowed")
        resp = httpx.get(url, timeout=timeout)
        body = resp.text[:max]
        headers = {k: v for k, v in resp.headers.items()}
        return {"status": resp.status_code, "headers": headers, "body": body}


    @mcp.tool("fs.list")
    def fs_list(path: str = ".") -> Dict[str, Any]:
        p = _resolve_fs(path)
        entries = []
        for child in p.iterdir():
            stat = child.stat()
            entries.append({
                "name": child.name,
                "is_dir": child.is_dir(),
                "size": stat.st_size,
            })
        return {"entries": entries}


    @mcp.tool("fs.read_text")
    def fs_read_text(path: str) -> str:
        p = _resolve_fs(path)
        return p.read_text()


    @mcp.tool("fs.write_text")
    def fs_write_text(path: str, text: str) -> Dict[str, Any]:
        if len(text.encode("utf-8")) > 128 * 1024:
            raise ValueError("Text too large")
        p = _resolve_fs(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
        return {"bytes": len(text.encode("utf-8"))}

    # @mcp.tool("csv.to_json")
    # def csv_to_json(csv: str, header: bool = True) -> Dict[str, Any]:  # noqa: A002
    #     reader = csv.reader(io.StringIO(csv))
    #     rows: List[Dict[str, str]] = []
    #     if header:
    #         try:
    #             headers = next(reader)
    #         except StopIteration:
    #             headers = []
    #         for row in reader:
    #             rows.append({h: v for h, v in zip(headers, row)})
    #     else:
    #         for row in reader:
    #             rows.append({str(i): v for i, v in enumerate(row)})
    #     return {"rows": rows}


    @mcp.tool("csv.from_json")
    def csv_from_json(rows: List[Dict[str, Any]], header: bool = True) -> str:
        if not rows:
            return ""
        output = io.StringIO()
        fieldnames = list(rows[0].keys())
        writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
        if header:
            writer.writeheader()
        writer.writerows(rows)
        return output.getvalue()
