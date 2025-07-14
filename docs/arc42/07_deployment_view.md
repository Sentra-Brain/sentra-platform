# 7. Deployment View

## Overview

This section describes how the Sentra Brain system is deployed in real-world environments. It clarifies the physical distribution of software components, networking requirements, and deployment models, with a focus on self-hosted installations.

---

## 7.1 Deployment Models

| Model                | Description                                      | Notes                                   |
|---------------------|--------------------------------------------------|-----------------------------------------|
| Self-Hosted         | Installed on client-owned hardware within private network. | Primary and recommended deployment.     |
| Hybrid (Optional)   | Core services self-hosted, some integrations via cloud (e.g., CRM, external data). | Under vendor-managed agreement only.    |

---

## 7.2 Deployment Topology

### Self-Hosted Topology Diagram

```mermaid
flowchart TD
    subgraph Client_Network["Client Private Network"]
        subgraph Sentra_Brain_Server["Sentra Brain Server"]
            API["API Gateway"]
            LLM["LLM Server (llama.cpp)"]
            RAG["RAG Engine (ChromaDB/Qdrant)"]
            MCP["MCP Server"]
            Auth[Internal Auth Service]
            n8n[Embedded n8n]
        end
        Frontend["User Frontend (Web App)"]
        AdminPanel[Admin Panel (client admins only)]
        VendorPanel[Vendor Control Panel (vendor super admins only)]
    end

    subgraph External_Connections["Optional External Services"]
        DataSources[External Data Sources]
        CRM_APIs[CRM/ERP APIs]
        Vendor_Monitoring[JGCarmona Monitoring Endpoint]
    end

    Frontend --> API
    AdminPanel --> API
    VendorPanel --> API
    VendorPanel --> n8n
    AdminPanel --> n8n
    API --> LLM
    API --> RAG
    API --> MCP
    API --> Auth
    API --> n8n
    RAG --> DataSources
    MCP --> CRM_APIs
    Vendor_Monitoring --> API
```
## 7.3 Deployment Considerations

- **Hardware Requirements:**  
  - Certified Workstation or Rack Server.  
  - Minimum GPU: NVIDIA RTX A6000 or equivalent.

- **Networking:**  
  - Internal access only for User Frontend and Admin Panel (client admins only).
  - Vendor Control Panel is accessible only to JGCarmona Consulting/vendor super admins for monitoring, licensing, and root configuration.
  - Embedded n8n is accessible via Admin Panel (client scope) and Vendor Control Panel (vendor scope).
  - Vendor monitoring endpoint secured via VPN or restricted IP filtering.

- **Security Controls:**  
  - Internal Auth Service is mandatory.  
  - No public API exposure except optional MCP integrations under strict control.  
  - Embedded n8n is accessible via Admin Panel (client scope) and Vendor Control Panel (vendor scope).

---
**Panel Access Notes:**
- **Admin Panel (client admins only):** For SME Administrators to manage their own Sentra Brain instance, including service monitoring, configuration, and client-scope n8n workflows.
- **Vendor Control Panel (vendor super admins only):** For JGCarmona Consulting to manage licensing, system health, root configuration, and vendor-scope n8n workflows.
- For all references to these panels, see [Section 12: Glossary](12_glossary.md).

- **Management and Maintenance:**  
  - JGCarmona Consulting is responsible for initial deployment, configuration, and ongoing monitoring.  
  - Clients may be granted limited admin access based on licensing agreements.

