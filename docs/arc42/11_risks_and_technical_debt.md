# 11. Risks and Technical Debt

## Overview

This section identifies key risks and areas of technical debt that may impact the stability, scalability, or maintainability of Sentra Brain. It also outlines mitigation strategies where applicable.

---

## 11.1 Identified Risks

| ID   | Risk Description                                           | Impact             | Mitigation Strategy                           |
|------|-----------------------------------------------------------|-------------------|-----------------------------------------------|
| R-01 | LLM backend performance and compatibility                  | Performance/Scale | vLLM is now the default backend; monitor for model compatibility and performance regressions. |
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
  vLLM deployment is now automated via Docker. llama.cpp remains available for lightweight or CPU-only scenarios.

- **MCP API Specification:**  
  Initial MCP servers may lack complete OpenAPI/Swagger specifications. This will be formalized to improve integration and maintainability.

- **Frontend and Admin UI Modularization:**  
  User Frontend and Admin Panel share deployment artifacts. Full modular separation (independent apps and services) is scheduled for future phases.

- **Embedded n8n Update Management (Future Phase):**  
  If activated, n8n updates require vendor-managed processes. Update handling and client-side access policies will be defined in Phase 2.


---

## 11.3 Continuous Risk Review

Risks and technical debt are reviewed on a regular basis by Juan G Carmona during each deployment and product phase update. Mitigation actions are prioritized according to business impact and client requirements.
