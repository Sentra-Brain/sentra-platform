# 9. Architectural Decisions – Sentra Brain (Phase 1 Baseline)

## Overview

This section summarizes and documents the core architectural decisions that define the Sentra Brain system for Phase 1. These decisions cover service structure, orchestration, deployment, and licensing mechanisms.

All items here are considered fixed for Phase 1. Future enhancements like workflow automation (n8n) and vendor control features will be addressed in later phases.

---

## Architectural Decision Table (Phase 1 Baseline)

| ADR #  | Topic                                         | Status    | Phase 1 Scope? | Notes                                      |
|--------|-----------------------------------------------|-----------|----------------|--------------------------------------------|
| 001    | LLM Backend Engine: llama.cpp Host-Based      | Final     | ✅ Yes         | Direct host execution for GPU efficiency    |
| 002    | Sentra API: Modular Orchestrator Design       | Final     | ✅ Yes         | FastAPI-based, layered (Chat, Auth, MCP Client) |
| 003    | MCP Server Architecture: Split Per Capability | Final     | ✅ Yes         | sentra-doc, sentra-crm, sentra-action       |
| 004    | RAG Engine: ChromaDB Default                  | Final     | ✅ Yes         | Local vector store                          |
| 005    | Auth Service: Internal Only (SQL + NoSQL)     | Final     | ✅ Yes         | Self-hosted Auth DB + Conversations DB      |
| 006    | Service Orchestration: Docker Compose         | Final     | ✅ Yes         | Small install model                         |
| 007    | Workflow Engine (n8n): Future Phase           | Planned   | ❌ No          | Explicitly postponed to Phase 2             |
| 008    | Deployment Model: Self-Hosted First           | Final     | ✅ Yes         | Hybrid optional, vendor-managed             |
| 009    | Monitoring & Licensing Mechanism              | Final     | ✅ Yes         | Health endpoint, no telemetry               |

---

## ADR 001 – LLM Backend Engine: llama.cpp Host-Based

**Decision:**  
Use llama.cpp running directly on the host OS (Ubuntu preferred) as the primary LLM server.

**Rationale:**  
- Maximize GPU efficiency and simplicity.
- Avoid Docker GPU binding complexities in Phase 1.

---

## ADR 002 – Sentra API: Modular Orchestrator Design

**Decision:**  
Implement Sentra API using FastAPI, structured into:

- **HTTP API Layer:** OpenAI-compatible endpoints, Admin UI, Auth endpoints.
- **Chat Orchestrator Layer:**  
  - ContextRouter (LLM / RAG / MCP dispatch)
  - PromptBuilder (history + system prompts)
  - ToolExecutor (MCP Client manager)
- **Knowledge Layer:**  
  - DocumentUploader  
  - IndexationManager (Embeddings → ChromaDB)
- **Auth Layer:**  
  - UserSlotManager (5 fixed slots max)  
  - SessionHandler (JWT or cookies)

**Rationale:**  
Clear separation of concerns, maintainability, SME-friendly stack.

---

## ADR 003 – MCP Server Architecture: Split Per Capability

**Decision:**  
Split MCP functionality into three independent services:

- **sentra-doc:** Document Search Tools  
- **sentra-crm:** CRM Lookup Tools  
- **sentra-action:** Email and Action Triggers  

**Rationale:**  
- Security: Isolate sensitive tool access per MCP server.  
- Deployment: Flexible hybrid setups (local + remote MCP servers).  
- Maintenance: Simpler versioning and debugging per MCP capability.

---

## ADR 004 – RAG Engine: ChromaDB Default

**Decision:**  
Use ChromaDB as the default local vector store in Phase 1.

**Rationale:**  
- Python ecosystem alignment.
- Simpler setup than alternatives like Qdrant or Weaviate.

---

## ADR 005 – Auth Service: Internal Only (SQL + NoSQL)

**Decision:**  
Implement an Internal Auth Service using:

- **SQL DB:** User credentials, configuration.
- **NoSQL DB:** Conversation logs, chat histories (JSON format).

**Rationale:**  
- Local data control.  
- Aligns with self-hosted privacy requirements.

---

## ADR 006 – Service Orchestration: Docker Compose

**Decision:**  
Use Docker Compose as the default orchestration tool for all services except llama.cpp.

**Rationale:**  
- Simple deployment for SMEs.  
- Consistency with Phase 1 “Small Install” scenario.

---

## ADR 007 – Workflow Engine (n8n): Future Phase

**Decision:**  
Workflow automation (n8n) will not be included in Phase 1 deployments.

**Rationale:**  
- Keep Phase 1 lean and focused.  
- Avoid unnecessary security exposure before admin workflows are formalized.

---

## ADR 008 – Deployment Model: Self-Hosted First

**Decision:**  
Self-hosted deployment is mandatory. Hybrid deployment is optional under vendor control.

**Rationale:**  
- Full data control for SMEs.  
- Consistent with Sentra Brain’s value proposition.

---

## ADR 009 – Monitoring & Licensing Mechanism

**Decision:**  
Implement a health monitoring and license validation endpoint (`/health`), only accessible by JGCarmona Consulting.

**Rationale:**  
- Enforce licensing.  
- Provide basic support monitoring without privacy compromises.

---
