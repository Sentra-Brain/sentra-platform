# 5. Building Block View

## Overview

This section provides a hierarchical decomposition of the Sentra Brain system into its main building blocks. Each block represents a key functional or technical component, illustrating how responsibilities are distributed and how components interact.

---

## Level 1: System Overview

```mermaid
graph TD
    Frontend[User Frontend]
    AdminPanel["Admin Panel (client admins only)"]
    VendorPanel["Vendor Control Panel (vendor super admins only)"]
    API[API Gateway]
    LLM["LLM Server (llama.cpp/vLLM)"]
    RAG["RAG Engine (ChromaDB/Qdrant)"]
    MCP["MCP Server"]
    Auth[Internal Auth Service]
    n8n[Embedded n8n Workflow Engine]
    DataSources[External Data Sources]
    CRMs[CRM/ERP APIs]

    Frontend --> API
    AdminPanel --> API
    VendorPanel --> API
    VendorPanel --> n8n
    API --> LLM
    API --> RAG
    API --> MCP
    API --> Auth
    AdminPanel --> n8n
    RAG --> DataSources
    MCP Server --> CRMs

```

## Level 2: Main Building Blocks and Responsibilities

| Building Block        | Description                                                        |
|----------------------|--------------------------------------------------------------------|
| **User Frontend**         | End-user web application (React + Tailwind). LLM queries, RAG searches. |
| **Admin Panel (client admins only)**      | Client-accessible administration interface for SME Administrators. Service monitoring, configuration, n8n access (client scope). |
| **Vendor Control Panel (vendor super admins only)** | Vendor-only admin interface for monitoring, licensing, and root configuration. |
| **API Gateway**      | Central routing point for all internal and external API requests. Handles authentication and forwarding. |
| **LLM Server**       | Runs local or hybrid large language models (llama.cpp, vLLM). Responds to queries from API Gateway. |
| **RAG Engine**       | Knowledge retrieval component using ChromaDB or Qdrant. Provides document search functionality. |
| **MCP Server**       | Model Context Protocol server. Exposes custom APIs for CRM, ERP, Office plugin integration. |
| **Auth Service**     | Internal authentication and authorization service. Manages user roles and secure API access. |
| **Embedded n8n**     | Workflow automation engine. Used for vendor-configured and (optionally) client-configured automations. |
| **External Data Sources** | Third-party systems providing knowledge or reference data to RAG. |
| **CRM/ERP APIs**     | Client-specific CRM, ERP, and internal tool integrations managed via MCP. |

---

## Building Block Relationships

- **Frontend + Admin Panel → API Gateway:** All user interactions pass through the central API layer.
- **API Gateway → Services (LLM, RAG, MCP, Auth):** API Gateway orchestrates requests and enforces access control.
- **n8n Access Restriction:** Embedded n8n is reachable only from the Admin Panel, not exposed via the general API.
- **Vendor Monitoring Endpoint:** `/health` or `/sentra-monitor` is exposed by API Gateway, secured and isolated.

---

## Notes

- All blocks are structured under a single repository using a monorepo layout for consistency:
  - `/apps/`: Frontend and Admin Panel apps.
  - `/services/`: LLM, RAG, MCP, Auth, n8n-related services.
  - `/deploy/`: Docker Compose/Kubernetes manifests, configuration.
  - `/docs/arc42/`: Architecture documentation.
  - `/website/`: Marketing and documentation frontend.
