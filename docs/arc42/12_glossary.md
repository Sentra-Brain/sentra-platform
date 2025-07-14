# 12. Glossary

## Purpose

This glossary defines key terms, acronyms, and system components used throughout the Sentra Brain architecture documentation. It ensures shared understanding among all stakeholders: developers, integrators, and clients.

---

## 12.1 Terms and Definitions

| Term / Acronym  | Definition                                                                                   |
|-----------------|----------------------------------------------------------------------------------------------|
| Sentra Brain    | Modular, self-hosted private AI platform developed and deployed by JGCarmona Consulting.     |
| LLM             | Large Language Model. AI model used for generating text responses and processing queries.     |
| llama.cpp       | Open-source LLM serving engine optimized for local GPU inference.                             |
| RAG             | Retrieval-Augmented Generation. Combines document search with LLM query completion.          |
| ChromaDB        | Default vector database engine used for implementing RAG functionality.                      |
| Qdrant          | Alternative vector database engine considered for future scaling needs.                       |
| MCP Server      | Model Context Protocol Server. Custom API layer handling LLM, RAG, and workflow orchestration.|
| n8n             | Embedded workflow automation tool used for internal process configuration and integrations.   |
| Auth Service    | Internal authentication service implementing OAuth2/OpenID standards.                         |
| Self-Hosted     | Deployment model where all Sentra Brain services run within the client’s private infrastructure.|
| Hybrid          | Deployment model combining self-hosted core services with optional controlled cloud integrations.|
| API Gateway     | Main entry point for all HTTP/gRPC requests. Routes traffic to LLM, RAG, MCP, etc.           |
| Admin Panel     | Client-accessible administration interface for SME Administrators (client’s own admins) to manage their Sentra Brain instance.|
| Vendor Control Panel | Vendor-only interface for license management, system health monitoring, and root configuration.|
| User Frontend   | Web-based chat or query interface for end users to access Sentra Brain AI capabilities.       |
| /health Endpoint| Secure vendor-only API endpoint used for license validation and system health monitoring.     |
| CRM/ERP         | Client Relationship Management / Enterprise Resource Planning systems integrated via MCP.     |


> **Note:** When referencing **Admin Panel** or **Vendor Control Panel** in this document, see this glossary section (12) for precise definitions and access scopes. 
> 
> - **Admin Panel:** Client admins only (SME Administrators)
> - **Vendor Control Panel:** Vendor super admins only (JGCarmona Consulting)


## 12.2 Vertical-Specific Terms (Examples)

| Vertical          | Term                | Meaning / Relevance                                  |
|-------------------|--------------------|-----------------------------------------------------|
| Law Firms         | Jurisprudence       | Relevant legal cases and decisions searchable via RAG.|
| Financial Agencies| Compliance Reports  | Regulatory documents processed via Sentra Brain.     |
| Industrial SMEs   | Internal Workflows  | Custom automation sequences configured via n8n.      |
| Healthcare        | Patient Data        | Sensitive information processed securely and privately.|
