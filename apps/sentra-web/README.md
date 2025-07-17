# Sentra Web (User Chat Interface)

This folder contains the source code and Docker configuration for the **Sentra Brain end-user frontend application**.

---

## Purpose

- Provides a secure chat and search interface for end-users:
  - LLM chat with optional RAG context (document search).
  - Document search independent of chat.
  - CRM/ERP data requests via MCP servers.
- Handles user authentication against the Sentra API.
- Displays user profile information and conversation history (where enabled).

---

## Functional Scope

| Feature                | Description                                                   |
|-----------------------|---------------------------------------------------------------|
| User Login            | Auth via Sentra API (SQL backend)                             |
| Chat with LLM         | Standard query submission                                     |
| Chat with RAG         | Select one or more knowledge bases (datasources)              |
| Document Search (RAG) | Search documents without chat flow                            |
| CRM/ERP Data Request  | Trigger MCP CRM/Action requests (future-ready)                |
| Responsive UI         | Mobile and desktop compatible                                 |

---

## Technology Stack

- **Frontend Framework:** React / Next.js
- **UI Styling:** Tailwind CSS
- **State Management:** Local Storage or Redux (if implemented)
- **Backend Connection:** REST API via Sentra API

---

## Runtime Architecture

- Communicates exclusively with Sentra API:
  - **Authentication:** Token-based (JWT or similar).
  - **Chat Flow:** User → API → LLM (+ optional RAG).
  - **Document Retrieval:** User → API → RAG Engine.
  - **CRM/ERP (MCP):** User → API → MCP Servers (sentra-crm, sentra-action).

For detailed runtime diagrams, see `/docs/arc42/06_runtime_view.md`.

---

## Development Workflow

```bash
npm install
npm run dev
```

- Uses port `3100` in development (see `docker-compose.dev.yml`).
- Mounted volumes enabled for live reload via Docker.

---

## Deployment Notes

- Production builds are created via:
  ```bash
  npm run build
  ```
- Final images are published as:
  ```
  sentrabrain.azurecr.io/sentra-web:latest
  ```
- Managed by `docker-compose.yml` (production) and `docker-compose.dev.yml` (development).

---

## Related Services

- **Backend API:** [services/sentra-api](../../services/sentra-api)
- **Admin Panel:** [apps/sentra-admin](../sentra-admin)

---