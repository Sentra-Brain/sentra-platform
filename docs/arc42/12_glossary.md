# 12. Glossary

## Purpose

This glossary defines key terms, acronyms, and system components used throughout the Sentra Brain architecture documentation. It ensures shared understanding among all stakeholders: developers, integrators, and clients.

---

## 12.1 Terms and Definitions

| Term / Acronym        | Definition                                                                                       |
|----------------------|--------------------------------------------------------------------------------------------------|
| Sentra Brain         | Modular, self-hosted private AI platform developed and deployed by JGCarmona Consulting.         |
| LLM                  | Large Language Model. AI model used for generating text responses and processing queries.         |
| llama.cpp            | Open-source LLM serving engine optimized for local GPU inference.                                 |
| RAG                  | Retrieval-Augmented Generation. Combines document search with LLM query completion.              |
| ChromaDB             | Default vector database engine used for implementing RAG functionality.                          |
| MCP Servers          | Modular Model Context Protocol Servers: split into few for better isolation. |
| Auth Service         | Internal authentication service implementing OAuth2/OpenID standards.                             |
| Self-Hosted          | Deployment model where all Sentra Brain services run within the client’s private infrastructure.  |
| Hybrid               | Deployment model combining self-hosted core services with optional controlled cloud integrations.  |
| API Gateway          | Sentra API. Main entry point for all HTTP/gRPC requests. Routes traffic to LLM, RAG, MCP Servers, etc. |
| Admin Panel          | Client-accessible administration interface for SME Administrators (client’s own admins).          |
| User Frontend        | Web-based chat or query interface for end users to access Sentra Brain AI capabilities.           |
| /health Endpoint     | Secure vendor-only API endpoint used for license validation and system health monitoring.         |
| CRM/ERP              | Client Relationship Management / Enterprise Resource Planning systems integrated via MCP Servers.  |
| Conversations DB     | Document-based NoSQL database storing chat histories and user interaction logs.                   |

> **Note:**  
> In Phase 1, features like the **Vendor Control Panel** and embedded **n8n** are documented as future-phase options and are not included in the core deployment baseline.

---

## 12.2 Vertical-Specific Terms (Examples)

| Vertical            | Term               | Meaning / Relevance                                     |
|--------------------|-------------------|--------------------------------------------------------|
| Law Firms          | Jurisprudence      | Relevant legal cases and decisions searchable via RAG. |
| Financial Agencies | Compliance Reports | Regulatory documents processed via Sentra Brain.       |
| Industrial SMEs    | Internal Workflows | Custom process sequences managed via Sentra Brain tools.|
| Healthcare         | Patient Data       | Sensitive information processed securely and privately. |
