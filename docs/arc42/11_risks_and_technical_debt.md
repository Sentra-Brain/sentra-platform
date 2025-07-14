# 11. Risks and Technical Debt

## Overview

This section identifies key risks and areas of technical debt that may impact the stability, scalability, or maintainability of Sentra Brain. It also outlines mitigation strategies where applicable.

---

## 11.1 Identified Risks

| ID   | Risk Description                                           | Impact             | Mitigation Strategy                           |
|------|-----------------------------------------------------------|-------------------|-----------------------------------------------|
| R-01 | Over-reliance on llama.cpp for LLM serving                | Performance/Scale | Evaluate vLLM or alternative backends for future phases. |
| R-02 | Single-vendor management of n8n workflows                 | Operational       | Define a controlled access model for client-side usage in Phase 2. |
| R-03 | ChromaDB scalability limitations                          | Performance       | Plan migration path to Qdrant or Weaviate if needed. |
| R-04 | Manual GPU configuration in self-hosted environments      | Complexity        | Provide deployment scripts and vendor support packages. |
| R-05 | MCP Server complexity and growth                          | Maintainability   | Refactor and modularize MCP logic early as features grow. |
| R-06 | Lack of formal CI/CD pipelines for client setups          | Deployment        | Implement Ansible or Docker Compose deploy scripts; document versioning strategy. |
| R-07 | Vendor-only monitoring perceived as privacy risk          | Client Trust      | Transparently document what is monitored; no user or document data is included. |
| R-08 | FastAPI performance bottlenecks under high concurrency    | Performance       | Evaluate Uvicorn/Gunicorn tuning, async optimizations, or migration to .NET MCP. |

---

## 11.2 Technical Debt Areas

- **LLM Service Bootstrapping:**  
  Current deployments require manual llama.cpp compilation and service setup. Automating this via scripts is pending.

- **MCP API Specification:**  
  Initial versions may lack full OpenAPI/Swagger documentation. Must be addressed to improve integration ease.

- **Frontend and Admin UI Separation:**  
  Both user frontend and admin panel share some assets and configurations. Clean separation is planned for Phase 2.

- **Embedded n8n Update Management:**  
  Updating the n8n instance requires manual intervention and is tied to vendor-managed access policies.

---

## 11.3 Continuous Risk Review

Risks and technical debt are reviewed on a regular basis by JGCarmona Consulting during each deployment and product phase update. Mitigation actions are prioritized according to business impact and client requirements.

---

> Maintainer: Juan G Carmona  
> Version: v0.1 – Draft Phase  
> Last Updated: 2025-07-14
