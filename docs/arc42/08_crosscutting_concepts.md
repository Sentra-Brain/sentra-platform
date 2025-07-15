# 8. Crosscutting Concepts

## Overview

This section captures the crosscutting architectural concepts applied throughout Sentra Brain’s design. These principles and mechanisms impact multiple system components and are essential for maintaining coherence, security, and maintainability.

---

## Security and Privacy

- **Self-Hosted First:** All core services operate within the client’s infrastructure. By default, Sentra Brain is designed for LAN-only or VPN-protected environments.
- **Internal Authentication Service:** Sentra API validates all user sessions and API tokens against the Auth DB (SQL + NoSQL).
- **Admin Tools Protection:** Vendor monitoring and workflow automation features are planned for future phases.
- **Role-Based Access Control:** Only authorized users can access sensitive areas like configuration or monitoring.
- **Encrypted Communication:** All internal and external API communication uses HTTPS and, where applicable, mutual TLS.

---

## Vendor Monitoring and Support Access

In future phases, Sentra Brain may include a dedicated Vendor Control Panel and embedded workflow engine (n8n). These features are not part of the core Phase 1 deployment baseline.

- **Health Monitoring Endpoint:**
  - Each Sentra Brain instance exposes a secure `/health` endpoint for service monitoring and license validation, restricted to JGCarmona Consulting systems.
  - Vendor Control Panel access mechanisms are planned for future phases.

- **License Validation:**
  - Periodic checks to validate licensing status are performed via the Vendor Control Panel.
  - This mechanism is opt-in for Community Edition and mandatory for Commercial Licensed deployments.

- **Client Privacy Assurance:**
  - Vendor access via the Vendor Control Panel is limited to technical metadata only.
  - No operational queries, user data, or private documents are ever transmitted.

---

## System Monitoring

- **Centralized Logs:** Application logs for LLM, RAG, MCP, and Admin UI are aggregated for easier debugging and auditing.
- **Metrics Exposure:** Internal service health endpoints expose basic status and resource usage. Standard formats such as `/metrics` may be provided, depending on client monitoring requirements.

---

## Consistency Mechanisms

- **API Versioning:** All internal and external APIs follow a versioned schema to avoid breaking changes.
- **Unified Error Handling:** Standardized error codes and responses across all services.
- **Configuration Management:** Centralized configuration files with environment-specific overrides (`/deploy/` folder).
- **Single Repository Monorepo:** Ensures alignment between services, frontend components, and deployment scripts.
