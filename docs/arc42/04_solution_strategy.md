**Community Fair-Use & Activation (Optional)**
- Free internal use for up to **5 named users** per org (Community Edition).
- Optional **activation** may assign an **anonymous Instance ID** for license validation.
- Commercial license required beyond fair-use thresholds.
# 4. Solution Strategy

## Overview

This section outlines the fundamental solution strategy behind Sentra Brain. It describes the key architectural decisions, modular structure, target verticals, and a proposed development roadmap to ensure clarity and alignment with both business and technical goals.

Sentra Brain is positioned as a private, modular AI platform designed for SMEs and professional environments, prioritizing full data control, compliance, and adaptability.

---

## Key Architectural Decisions

- **Modular Architecture:** Independent services for LLM Serving, RAG Engine, MCP Servers (split by capability: TBD), Admin Panel.
- **Self-Hosted by Default:** Primary deployment model is on-premise or private cloud, ensuring no external dependency for core functions.
- **LLM Serving Engine:** Compatible with llama.cpp, vLLM, and multiple GGUF format models, including GPT, Qwen, Llama families.
- **Secure MCP Integration:** Provides a controlled API layer for CRM, ERP, Office plugins, and other internal systems, split into dedicated MCP services per capability.
- **Document Search (RAG):** Integration with ChromaDB for private knowledge base retrieval.
- **Internal Authentication and Session Handling:** Using SQL database for user credentials/configuration and NoSQL database (MongoDB) for chat histories.
- **Single-Repository Monorepo:** Unified structure `/apps/`, `/services/`, `/deploy/`, `/docs/arc42/`, `/frontends/website/`.
- **Enterprise-Grade Security:** Designed for GDPR, HIPAA, and ISO27001 compliance.
- **Certified Hardware:** Official deployment packages include Sentra Brain-certified hardware.
- **Workflow Automation (Future Phase):** Embedded n8n instance for internal process automation planned for future development (not part of Phase 1 baseline).

---

## Primary Target Verticals

| Sector                    | Use Case Description                                                                |
|--------------------------|------------------------------------------------------------------------------------|
| **Law Firms**            | Draft contracts, analyze jurisprudence, automate legal tasks with GDPR compliance.  |
| **Financial Agencies**   | Analyze reports, summarize regulations, process sensitive data securely.            |
| **Industrial SMEs**      | Optimize internal processes, customer support, documentation using private AI.      |
| **Healthcare**           | Handle patient records, internal knowledge, decision support without external dependencies. |
| **Public Sector**        | Vendor-independent AI services for public administration, respecting national security policies. |
| **Any Professional Environment** | Sentra Brain adapts to your company's needs. Contact us to explore custom integrations. |

---

## Modular Architecture Overview

- **LLM Serving Engine:** Run large language models locally or hybrid. Compatible with GPT, Qwen, Llama, and more.
- **MCP Integration:** Secure API layer split into dedicated services (TBD) for CRM, ERP, and internal tool integration.
- **Document Search (RAG):** Private document search powered by ChromaDB.
- **Internal Authentication & Chat History:** SQL + NoSQL database structure for user management and conversation storage.
- **Enterprise-Grade Security:** On-premise or hybrid deployment. GDPR, HIPAA, ISO27001 ready.
- **Certified Hardware & Support:** Official packages with certified hardware and professional consulting.
- **Custom Automations (Future Phase):** Workflow integration using embedded n8n is planned for a later release.


---

## Development Roadmap Proposal

| Phase       | Scope                                                                                                                              | Estimated Duration |
| ----------- | ---------------------------------------------------------------------------------------------------------------------------------- | ------------------ |
| **Phase 1** | Base Architecture, LLM + RAG + MCP Server(s), Single UI, Internal Auth Service (SQL + NoSQL) | 4–6 weeks          |
| **Phase 2** | Admin Panel Development, Embedded n8n Integration (Workflow Automation), Logs and Monitoring                                       | 3–4 weeks          |
| **Phase 3** | Certified Hardware Packages, Deployment Tooling (Docker/K8s), Installer Scripts                                                    | 2–3 weeks          |
| **Phase 4** | Hybrid Deployment Enhancements, External Auth (optional), Advanced Security Audits                                                 | 3–4 weeks          |
| **Phase 5** | Official Client Launch, Documentation Finalization, Support Channel Setup                                                          | 2 weeks            |
