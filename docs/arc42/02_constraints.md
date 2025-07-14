# 2. Constraints

## Overview

This section outlines the constraints that affect the design and development of the Sentra Brain architecture. Constraints include both external factors, such as regulatory or business mandates, and internal factors, such as chosen technologies, deployment models, and operational policies.

These constraints define the framework within which all architectural decisions for Sentra Brain are made, ensuring alignment with client expectations, regulatory standards, and technical feasibility.

---

## External Constraints

- **Regulatory Compliance**  
  All components and workflows must comply with GDPR and relevant data protection laws applicable to SME clients in Europe.

- **Licensing Model**  
  Sentra Brain operates under a dual model:  
  - **Open Core (AGPLv3)**: Up to 3 users/devices, self-hosted by the community.  
  - **Commercial License**: Hardware + software package sold exclusively by JGCarmona Consulting S.L.U.

- **Deployment Restrictions**  
  Public SaaS hosting is not permitted for core functions. Installations must be self-hosted, either on-premises or within private cloud environments controlled by the client.

- **Client Profile**  
  The architecture must prioritize ease of use and maintainability for SMEs, not large enterprises or consumer markets.

---

## Internal Constraints

- **Technology Stack Standardization**  
  Core technologies are pre-defined and locked-in:  
  - Backend: Python (FastAPI) and/or C# (.NET)  
  - LLM Serving: llama.cpp or vLLM (GGUF format models)  
  - RAG Layer: ChromaDB or Qdrant  
  - Frontend: React + Tailwind CSS  
  - Workflow Automation: Embedded n8n (admin access only)

- **Repository Structure**  
  The project must maintain a single-repository structure, organized as:  
  `/apps/`, `/services/`, `/deploy/`, `/docs/arc42/`, `/website/`.

- **Hardware Requirements**  
  Minimum baseline hardware for full deployment:  
  - NVIDIA RTX A6000 or equivalent for LLM serving  
  - At least 64 GB system RAM  

- **Security Policies**  
  - VPN or LAN-only access by default  
  - Admin tools such as n8n and Admin Panel restricted to authenticated system administrators  
  - Internal API keys must control access between components  

---

## Security, Trust, and Data Protection

One of Sentra Brain's foundational constraints is **operating as a standalone, private system within the client's controlled network environment**.

- **Data Residency**  
  All user data, model queries, logs, and configuration files remain strictly inside the client's infrastructure. No data is sent or shared with external cloud services or third-party providers by default.

- **Controlled Internet Access**  
  The system may access the Internet:  
  - To retrieve external information (e.g., via RAG or browsing agents).  
  - To interact with client-authorized proprietary systems (CRM, ERP).  
  Internet access is always controlled and audited. No unauthorized external communications are allowed.

- **No Data Leakage Guarantee**  
  Sentra Brain is explicitly designed with this trust model as a primary goal:  
  **Zero data leakage by architecture and by policy.**

- **Security Assurance Measures**  
  - VPN, firewall, and network segmentation enforcement.  
  - Internal-only API communication between modules.  
  - Embedded n8n and Admin Panel restricted to authorized administrators only.

---

> Maintainer: Juan G Carmona  
> Version: v0.1 – Draft Phase  
> Last Updated: 2025-07-14
