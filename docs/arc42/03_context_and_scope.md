
# 3. Context and Scope

## Overview

This section describes the context and scope of the Sentra Brain system, outlining its interactions with external actors, systems, and technical environments. It provides a high-level understanding of Sentra Brain's role within its business and technical environment.

## Business Context

Sentra Brain is designed to provide advanced AI-driven services for knowledge management, retrieval, and automation. It serves various stakeholders, including end-users, administrators, and external partner systems, enabling seamless integration and efficient workflows.

### Business Context Diagram

```mermaid
graph TD
    subgraph External_Actors["External Actors"]
        User[End User]
        Admin[Administrator]
        Partner[External Partner System]
    end

    subgraph Sentra_Brain["Sentra Brain System"]
        SentraBrain[Sentra Brain Platform]
    end

    User -->|Uses| SentraBrain
    Admin -->|Manages| SentraBrain
    Partner -->|Integrates with| SentraBrain
```


## Technical Context

Sentra Brain operates as a modular system composed of loosely coupled services, exposed through a central API Gateway. Its primary deployment model is self-hosted within the client's private infrastructure. Interaction with external services, such as external data sources or third-party APIs, is optional and always controlled. Hybrid deployment models may be considered in future phases.

### Technical Context Diagram

```mermaid
graph TD
    subgraph Client_Interface["Sentra Brain UI"]
        Frontend[User Frontend]
        AdminPanel[Admin Panel]
    end

    subgraph Sentra_Brain_System["Sentra Brain System"]
        API[API Gateway]
        LLM[LLM Server llama.cpp]
        RAG[RAG Engine ChromaDB/Qdrant]
        MCP[MCP Server Python or .NET]
        Auth[Internal Auth Service]
    end

    subgraph External_Services["External Services"]
        DataSources[External Data Sources]
        CRMs[Third Party CRM or ERP APIs]
    end

    Frontend -->|REST/GraphQL| API
    AdminPanel -->|REST/GraphQL| API

    API -->|gRPC/REST| LLM
    API -->|gRPC/REST| RAG
    API -->|gRPC/REST| MCP
    API -->|OAuth2/OpenID| Auth
    RAG -->|Fetches| DataSources
    MCP -->|Integrates| CRMs
```
