# Sentra API (Orchestrator + Auth + MCP Client)

This folder contains the source code and Docker configuration for the **Sentra Brain backend API service**.

---

## Purpose

- Acts as the central orchestrator for all Sentra Brain requests.
- Manages user authentication and session control.
- Routes chat queries, document search requests, and MCP calls:
  - Forwards chat + RAG context to LLM Server.
  - Retrieves documents from RAG Engine (ChromaDB).
  - Invokes MCP Servers for CRM/ERP data or action triggers.

---

## Functional Scope

| Feature                   | Description                                    |
|--------------------------|------------------------------------------------|
| User Authentication      | Login, token validation via SQL database      |
| Chat Orchestration       | Handles chat flow logic with or without RAG    |
| RAG Query Integration    | Communicates with ChromaDB to retrieve context |
| MCP Client Layer         | Connects to MCP servers (CRM, Action)          |
| API Security             | Token validation and permission checks         |
| Extensible Architecture  | FastAPI + modular service layers               |

---

## Technology Stack

- **Backend Framework:** Python 3.13 + FastAPI
- **Database:**:
  - PostgreSQL (Auth and configuration)
  - MongoDB (Conversation history and chat metadata)
- **Vector Store:** ChromaDB (external service)
- **LLM Backend:** vLLM (default)
- **State Management:** Token/session control via SQL + NoSQL
- **Container Runtime:** Docker

---

## Runtime Architecture

- Acts as intermediary between:
  - **Frontend:** Sentra Web / Sentra Admin
  - **LLM Server:** via HTTP
  - **RAG Engine:** via HTTP (ChromaDB REST API)
  - **MCP Servers:** via REST or gRPC (depending on MCP type)

For detailed runtime diagrams, see `/docs/arc42/06_runtime_view.md`.

---

## Development Workflow

```bash
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8100
```

- Uses port `8100` in development (see `docker-compose.dev.yml`).
- Supports live reload when mounted via Docker volume.

---

## Deployment Notes

- Production images are published as:

```
sentrabrain.azurecr.io/sentra-api:latest
```

- Managed by `docker-compose.yml` (production) and `docker-compose.dev.yml` (development).
- External services like vllm, ChromaDB, and MCP must be available at runtime.

---

## Related Services

- **Frontend:** [frontends/sentra-web](../../frontends/sentra-web)
- **Admin Panel:** [frontends/sentra-admin](../../frontends/sentra-admin)
- **RAG Engine:** [external - ChromaDB]
- **MCP Servers:** TBD


---