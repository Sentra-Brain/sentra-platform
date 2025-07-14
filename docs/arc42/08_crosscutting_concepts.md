# 8. Crosscutting Concepts

## Overview

This section captures the crosscutting architectural concepts applied throughout Sentra Brain’s design. These principles and mechanisms impact multiple system components and are essential for maintaining coherence, security, and maintainability.

---

## Security and Privacy

- **Self-Hosted First:** All core services operate within the client’s infrastructure. By default, Sentra Brain is designed for LAN-only or VPN-protected environments.
- **Internal Authentication Service:** Local auth system managing access to both frontend interfaces and API endpoints.
- **Admin Tools Protection:** Embedded n8n and Admin Panel are restricted to authenticated client administrators. Vendor Control Panel is restricted to vendor super admins. Access to these tools is never exposed publicly.
- **Role-Based Access Control:** Only authorized users can access sensitive areas like configuration or monitoring.
- **Encrypted Communication:** All internal and external API communication uses HTTPS and, where applicable, mutual TLS.

---

## Vendor Monitoring and Support Access

Sentra Brain installations include a controlled vendor-access mechanism via the Vendor Control Panel to ensure service health monitoring and license validation:

- **Health Monitoring Endpoint:**
  - Each Sentra Brain instance exposes a secure `/health` or `/sentra-monitor` endpoint, accessible only via the Vendor Control Panel by JGCarmona Consulting.
  - This endpoint is protected using internal API keys or mutual TLS.
  - Exposed data includes instance status, usage metrics, and license validation tokens — never sensitive client or user data.

- **License Validation:**
  - Periodic checks to validate licensing status are performed via the Vendor Control Panel.
  - This mechanism is opt-in for Community Edition and mandatory for Commercial Licensed deployments.

- **Client Privacy Assurance:**
  - Vendor access via the Vendor Control Panel is limited to technical metadata only.
  - No operational queries, user data, or private documents are ever transmitted.

---

## System Monitoring

- **Centralized Logs:** Application logs for LLM, RAG, MCP, and Admin UI are aggregated for easier debugging and auditing.
- **Metrics Exposure:** Internal Prometheus-compatible endpoints expose resource usage and service health.
- **Admin Notifications:** System administrators can configure email or webhook-based alerts via embedded n8n for key events.

---

## Consistency Mechanisms

- **API Versioning:** All internal and external APIs follow a versioned schema to avoid breaking changes.
- **Unified Error Handling:** Standardized error codes and responses across all services.
- **Configuration Management:** Centralized configuration files with environment-specific overrides (`/deploy/` folder).
- **Single Repository Monorepo:** Ensures alignment between services, frontend components, and deployment scripts.
