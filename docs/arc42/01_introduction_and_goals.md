# 1. Introduction and Goals

## Purpose

This section outlines the primary goals and strategic purpose of the Sentra Brain platform. It aims to align all stakeholders around its core objectives: delivering a private, modular AI system for SMEs that ensures full control over data, compliance, and system customization.

Sentra Brain exists to address a clear market need:  
> **Cloud-based AI services force companies to give up control over their data, intellectual property, and client information.**  

With increasing regulatory demands (GDPR, HIPAA, ISO27001), Sentra Brain provides a solution that puts ownership and control back in the hands of its users.

- **Your AI, your rules:** Install your own private AI server with no external dependencies or hidden costs.
- **Total Privacy:** All operations occur within the client’s infrastructure — fully compliant by design.
- **Flexible Integration:** Compatible with CRM, ERP, custom workflows, and automations.
- **No Limits:** Local models, no restricted tokens, and no pay-per-use billing models.

This philosophy guides both technical and business decisions throughout the system architecture.

## Key Stakeholders

| Stakeholder            | Role                     | Expectations                                        |
|-----------------------|-------------------------|----------------------------------------------------|
| JGCarmona Consulting   | Vendor & Integrator      | Provide turnkey deployment, support, and licensing |
| SME Administrators     | Platform Users           | Access private AI capabilities securely            |
| SME End Users          | Platform Users           | Access private AI capabilities securely            |
| Regulatory Authorities | Compliance Auditors      | Ensure GDPR and security standards are met         |

## Operating Model and Service Approach

Sentra Brain is not a purely self-service platform. Its deployment and configuration follow a controlled model managed exclusively by JGCarmona Consulting S.L.U. to ensure security, consistency, and support quality.

- **Vendor-Managed Installation:**  
  JGCarmona Consulting handles hardware provisioning, system installation, and initial configuration based on the client's vertical and requirements.

- **Pre-Configured Workflows:**  
  Workflow automation via n8n or similar tools is prepared and maintained by JGCarmona Consulting. Access to modify or extend these workflows may be opened to SME Administrators in future versions.

- **Maintenance and Support Services:**  
  Ongoing updates, security patches, and operational support are provided under a commercial licensing agreement.

- **Controlled Monitoring:**  
  Each Sentra Brain instance includes a protected monitoring mechanism (e.g., secure `/health` endpoint or encrypted telemetry) accessible only to JGCarmona Consulting for service health checks and license validation. This is explicitly designed to respect client privacy and regulatory compliance while enabling essential vendor support.

## Top Quality Goals

- **Privacy:** Guarantee that all AI queries and data processing occur locally or within controlled hybrid setups.
- **Modularity:** Allow flexible integration, replacement, or scaling of LLM, RAG, and MCP components.
- **Maintainability:** Provide clear separation of services, easy update mechanisms, and accessible admin tools.
- **Reliability:** Ensure stable, predictable operation with minimal downtime.
- **Security:** Restrict access through proper authentication, internal API keys, and private admin tools like n8n.

These goals shape all design and architecture decisions documented in the following sections.
