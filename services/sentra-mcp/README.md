# Sentra MCP Server (`sentra-mcp`)

This service exposes external tools ("skills") to the Sentra API using the FastMCP protocol. It allows the LLM to call tools like `web.search` or `web.fetch` via structured tool calls.

First tool implemented: **Internet Search (`web.search`)**.

---

## Key Details

* **Protocol**: FastMCP (HTTP transport)
* **Port**: `8200`
* **Transports**: HTTP (tool calls), `/health`, `/metrics`
* **Location**: `services/sentra-mcp`
* **Code Root**: `sentra_mcp/`

---

## Tool Overview

### `web.search(query: str, top_k: int = 5, recency_days: int = 60)`

Performs real-time web search using a backend API (Brave, Google CSE, etc.). Returns:

```json
[
  {"title": "Title", "url": "https://...", "snippet": "..."},
  ...
]
```

### (Planned) `web.fetch(url: str, max_chars: int = 8000)`

Fetches readable content from a public web URL. (Disabled by default.)

---

## Environment Variables (`.env`)

Example additions:

```env
# Search Provider (DuckDuckGo)

WEBSEARCH_MAX_RESULTS=5
WEBSEARCH_RECENCY_DAYS=60
```

---

## Docker Compose (Already Set Up)

```yaml
sentra-mcp:
  build:
    context: ../
    dockerfile: services/sentra-mcp/Dockerfile
  image: sentra-mcp:dev
  container_name: sentra-mcp
  ports:
    - "8200:8200"
    - "5681:5681"   # debugpy
    - "8080:8080"   # metrics
  volumes:
    - ../services/sentra-mcp:/app
    - ../core/sentra-core:/core/sentra-core
    - ${HOME}/sentra-knowledge:/mnt/sentra_knowledge:rw
  networks:
    - sentrabrain-dev-net
  env_file:
    - ../services/sentra-mcp/.env
```

---

## Local Dev

```bash
docker compose -f docker-compose.dev.yml up sentra-mcp
```

Healthcheck:

```bash
curl http://localhost:8200/health
```

---

## File Structure (Important parts)

```
sentra_mcp/
├── main.py            # FastMCP + FastAPI entrypoint
├── tools/
│   └── web.py         # web.search tool
├── config.py          # env loading
├── tools_registry.py  # Registers all the tools...
```

---

## Related Features

* **#78** Internet Search Tool (First MCP Skill)
* **#62** MCP Skills – Generalized skill orchestration
* **#76** Admin – Skill and MCP Server Management

---

This README will evolve as more tools and features are added. For now, this service provides the foundation for external tool execution in Sentra Brain via FastMCP.
