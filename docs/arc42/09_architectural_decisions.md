# 9. Architectural Decisions – Sentra Brain

## Overview

This section documents the key architectural decisions that shape the design and implementation of Sentra Brain. Each decision includes context, alternatives, and implications to ensure traceability and clarity.

---

## ADR 001 – Use llama.cpp as LLM Serving Engine

- **Status:** Decided  
- **Date:** 2025-07-14  

### Context  
Sentra Brain requires a private, self-hosted LLM serving engine with GPU acceleration, full local control, and no dependency on external SaaS services.

### Decision  
Use **llama.cpp** compiled and optimized for target GPUs (RTX A6000) as the LLM backend.

### Alternatives Considered  
- vLLM (Python-based, better batching but more resource-heavy)  
- GPT-4-turbo via API (rejected for privacy/compliance reasons)

### Consequences  
- Local GPU management required  
- MCP must handle HTTP requests to llama.cpp directly  

---

## ADR 002 – MCP Server Will Be Custom-Built Using FastAPI + LlamaIndex  

- **Status:** Decided  
- **Date:** 2025-07-14  

### Context  
We need a middle layer for routing requests, orchestrating RAG + LLM + Automations, and exposing a unified API for frontend and other systems.  

After reviewing multiple options for quick PoC and maintainability:  

| Stack                | Pros                                       | Cons                            |
|---------------------|--------------------------------------------|---------------------------------|
| FastAPI + LlamaIndex | Maximum control, fast setup, modular       | Manual flow handling required   |
| LangChain Agents    | Integrated tool-use, active community      | Heavier, more dependencies      |
| Haystack            | Focused Q&A pipelines                      | Less flexible for custom logic  |

### Decision  
We will build the **custom MCP Server using FastAPI combined with LlamaIndex** as the RAG orchestration library.  

This maximizes control and clarity while keeping the initial stack lightweight and manageable.

### Alternatives Considered  
- LangChain (kept as optional integration for future tools)  
- Haystack (not flexible enough for custom workflows)

### Consequences  
- Total control over orchestration logic and endpoints  
- Responsibility for building API specs, RAG logic, and admin interface falls on us  
- Simple and modular approach that aligns with Sentra Brain’s self-hosted philosophy


---

## ADR 003 – Use Docker Compose for Service Orchestration  

- **Status:** Decided  
- **Date:** 2025-07-14  

### Context  
Sentra Brain comprises several components that need to be deployed consistently: MCP Server, RAG Engine, Frontend, Admin Panel, and optional services.

### Decision  
Use **Docker Compose v3+** for orchestrating these services in initial deployments.

### Alternatives Considered  
- Kubernetes (planned for future scaling phases)

### Consequences  
- Simpler setup for SME environments  
- Manual GPU binding required for llama.cpp (see ADR 004)

---

## ADR 004 – LLM Server (llama.cpp) Runs on Host OS, Not Docker  

- **Status:** Decided  
- **Date:** 2025-07-14  

### Context  
Direct GPU access and simpler system resource management are essential.

### Decision  
Run llama.cpp **directly on the host OS (Ubuntu 24.04 preferred)** instead of containerized.

### Alternatives Considered  
- Docker + NVIDIA runtime (adds complexity and overhead)

### Consequences  
- Deployment scripts must handle llama.cpp as a system service  
- MCP connects via host IP/port  

---

## ADR 005 – ChromaDB as Default RAG Engine  

- **Status:** Tentative  
- **Date:** 2025-07-14  

### Context  
A local vector database is needed to enable document retrieval and knowledge base search.

### Decision  
Use **ChromaDB** as the initial RAG engine due to simplicity and Python ecosystem alignment.

### Alternatives Considered  
- Qdrant (better clustering but heavier)  
- Weaviate (overkill for initial scope)

### Consequences  
- MCP must integrate using ChromaDB’s Python client  
- Migration to Qdrant or Weaviate may be evaluated for larger clients  

---

## ADR 006 – Internal Authentication Service  

- **Status:** Final  
- **Date:** 2025-07-14  

### Context  
Sentra Brain must manage access control independently of external providers.

### Decision  
Use an **Internal Auth Service** implementing OAuth2 or OpenID standards, self-hosted alongside core services.

### Alternatives Considered  
- Google, Microsoft, or Okta integration (postponed)

### Consequences  
- Total control over user access  
- Simpler compliance alignment (GDPR, HIPAA)

---

## ADR 007 – Embedded n8n Access Model  

- **Status:** Final  
- **Date:** 2025-07-14  

### Context  
Sentra Brain includes embedded workflow automation via n8n, but unrestricted admin access could compromise system integrity.

### Decision  
**Restrict n8n access to JGCarmona Consulting personnel by default.**  
Client administrators may be granted access in controlled environments in future versions.

### Alternatives Considered  
- Fully open access (rejected for security and licensing control reasons)

### Consequences  
- Protects vendor-managed service model  
- Reduces support overhead in SME environments  

---

## ADR 008 – Deployment Model: Self-Hosted First, Hybrid Optional  

- **Status:** Final  
- **Date:** 2025-07-14  

### Context  
Sentra Brain’s value proposition is based on full data control and privacy.

### Decision  
**Self-hosted deployment is mandatory.** Hybrid/cloud integrations are optional and must be vendor-managed.

### Alternatives Considered  
- Cloud-first model (rejected due to privacy non-compliance)

### Consequences  
- Hardware and setup included in service package  
- Monitoring and licensing mechanisms must operate independently from public cloud services  

---

## ADR 009 – Monitoring and Licensing Mechanism  

- **Status:** Draft  
- **Date:** 2025-07-14  

### Context  
Sentra Brain must enforce licensing and provide remote health monitoring while respecting client privacy.

### Decision  
**Implement a vendor-controlled `/health` endpoint** accessible only by JGCarmona Consulting via VPN or secure IP whitelisting.

### Alternatives Considered  
- Full telemetry (rejected)  
- Manual offline validation (less practical)

### Consequences  
- Basic license verification without exposing sensitive client data  
- Ensures service availability monitoring for support purposes  

---

> Maintainer: Juan G Carmona  
> Version: v0.1 – Consolidated  
> Last Updated: 2025-07-14
