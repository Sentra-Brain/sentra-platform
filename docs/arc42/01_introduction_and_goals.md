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
| Juan G. Carmona       | Maintainer & Publisher     | Publish releases, docs; offer optional commercial licensing & support |
| SME Administrators     | Platform Users           | Access private AI capabilities securely            |
| SME End Users          | Platform Users           | Access private AI capabilities securely            |
| Regulatory Authorities | Compliance Auditors      | Ensure GDPR and security standards are met         |

## Operating Model and Service Approach


Sentra Brain supports **self-service deployment** (on-prem or private cloud). Community Edition is open and installable by anyone; commercial terms apply when usage exceeds the community fair-use thresholds.

- **Installation Options:** Self-service is supported. Assistance is optional (consultants/contributors may help on a project basis).
- **Pre-Configured Workflows (optional):** Reference automations (e.g., n8n) are offered as templates; admins can adopt, change, or remove them.
- **Maintenance & Updates:** Community Edition receives public releases. Commercial deployments can add SLAs and assisted upgrades.
- **Activation (optional, future):** A lightweight flow may provide an **anonymous Instance ID** to validate licensing and update eligibility. **No application content** is transmitted—only license/version metadata.

## Top Quality Goals

- **Privacy:** Guarantee that all AI queries and data processing occur locally or within controlled hybrid setups.
- **Modularity:** Allow flexible integration, replacement, or scaling of LLM, RAG, and MCP components.
- **Maintainability:** Provide clear separation of services, easy update mechanisms, and accessible admin tools.
- **Reliability:** Ensure stable, predictable operation with minimal downtime.
- **Security:** Restrict access through proper authentication, internal API keys, and private admin tools like n8n.

### Scope Clarification (Phase 1)

- **MCP Layer:** Phase 1 explicitly separates MCP into independent capability-focused services (TBD) to enhance security, scalability, and maintenance.
- **Workflow Automation:** Embedded workflow automation (e.g., n8n) is considered optional and planned for future implementation beyond Phase 1.

These goals shape all design and architecture decisions documented in the following sections.
