# 6. Runtime View

## Overview

This section describes typical runtime scenarios in Sentra Brain, focusing on how the system’s main components interact at runtime. It highlights request flows for core use cases: LLM Query Processing, Document Retrieval (RAG), .and (future) Workflow Execution via n8n.

---

## 6.1 LLM Query with RAG Context

**Scenario:**  
A user submits a question that may require both knowledge retrieval (RAG) and LLM response. Sentra Brain dynamically decides whether to use RAG based on user-selected datasources or system configuration.

**Step-by-Step Flow:**

1. **User Frontend → Sentra API**
    - REST/GraphQL request with the user query.
    - Authenticated via Sentra API against Auth DB (SQL).
    - User may specify active datasources or knowledge contexts via UI.

2. **Sentra API → RAG Engine (Conditional)**
    - If one or more datasources are selected, the API submits a search query to retrieve relevant documents or context snippets from the RAG Engine.
    - If no datasources are selected, this step is skipped.

3. **Sentra API → LLM Server (llama.cpp)**
    - API forwards the original query plus any retrieved RAG context as a combined prompt.
    - If RAG was bypassed, only the raw query is forwarded.
    - LLM processes the input and generates the final answer.

4. **LLM Server → Sentra API → User Frontend**
    - LLM response is sent back to the user.

### Sequence

```mermaid
sequenceDiagram
    participant User as User Frontend
    participant API as Sentra API
    participant Auth as Auth Service
    participant RAG as RAG Engine
    participant LLM as LLM Server

    User->>API: User Query + Datasources (REST/GraphQL)
    API->>Auth: Validate Token
    alt Datasources Selected
        API->>RAG: Retrieve Relevant Documents
        RAG-->>API: Retrieved Context
    else No Datasources Selected
        Note over API: Skip RAG Step
    end
    API->>LLM: Query (+ Context if available)
    LLM-->>API: LLM Response
    API-->>User: Final Answer
```


---

## 6.2 Document Retrieval (RAG) Scenario

**Scenario:**  
A user requests information that requires document search via the RAG Engine.

**Step-by-Step Flow:**

1. **User Frontend → Sentra API**  
   - Search query submitted.

2. **Sentra API → RAG Engine (ChromaDB/Qdrant)**  
   - API forwards the request to RAG for document similarity search.

3. **RAG Engine → External Data Sources (Optional)**  
   - If configured, RAG may fetch or update indices using external data sources.

4. **RAG Engine → Sentra API → User Frontend**  
   - Search results returned through the API.
### Sequence

```mermaid
sequenceDiagram
    participant User as User Frontend
    participant API as Sentra API
    participant Auth as Auth Service
    participant LLM as LLM Server
    participant RAG as RAG Engine

    User->>API: REST/GraphQL Query
    API->>Auth: Validate Token
    API-->>User: Query Result

    User->>API: Search Query
    API->>RAG: Document Retrieval
    RAG-->>API: Search Results
    API-->>User: Search Result

```

### 6.2.2 CRM/ERP Data Retrieval (MCP) Scenario

**Scenario:**  
 A user or an automated workflow (future feature) requests structured business data (e.g., customer details, sales orders) via Sentra Brain’s dedicated MCP Servers.

**Step-by-Step Flow:**

1. **User Frontend or (Future) n8n → Sentra API**  
   - Request for CRM/ERP data is initiated by a user through the frontend or, in future phases, via an automated workflow (n8n integration).

2. **Sentra API → MCP Servers**  
   - Sentra API forwards the request using gRPC or REST to the appropriate MCP Server, depending on the requested capability.

3. **MCP Server → CRM/ERP APIs**  
   - MCP performs necessary queries or actions on behalf of Sentra Brain.

4. **MCP Server → Sentra API → User Frontend or n8n**  
   - The response is routed back to the originator, maintaining access control and auditability.

### Sequence

```mermaid
sequenceDiagram
    participant User as User Frontend
    participant API as Sentra API (FastAPI)
    participant MCP_CRM as Sentra-CRM MCP
    participant MCP_Action as Sentra-Action MCP
    participant CRM as CRM/ERP APIs

    User->>API: Request CRM/ERP Data
    alt CRM Data Request
        API->>MCP_CRM: Forward Request
        MCP_CRM->>CRM: Query CRM/ERP System
        CRM-->>MCP_CRM: Response
        MCP_CRM-->>API: Forward Response
    else Action Request
        API->>MCP_Action: Forward Request
        MCP_Action->>CRM: Trigger Action
        CRM-->>MCP_Action: Acknowledge
        MCP_Action-->>API: Forward Response
    end
    API-->>User: Data Result

```

**Notes:**
- Same authentication and access control principles apply.
- MCP acts as a security and compatibility layer, avoiding direct exposure of external APIs to the frontend.
---

## 6.3 Vendor Workflow Execution (n8n) Scenario

**Scenario:**  
A vendor super admin triggers or schedules an internal automation workflow via n8n using the Vendor Control Panel.

**Step-by-Step Flow:**

1. **Vendor Control Panel → n8n**  
   - Vendor accesses the embedded n8n instance directly (internal network, authenticated, vendor scope).

2. **n8n → MCP Server / External APIs**  
   - Workflows may trigger actions via MCP Server or direct external API calls.

3. **n8n → Notification Channels**  
   - Example: webhook call, email notification to vendor admins, or database update.

**Notes:**  
- n8n access for vendor-level automations is managed via the Vendor Control Panel and restricted to vendor super admins.  
- Client administrators may gain access in future versions under controlled conditions.
### Sequence

```mermaid
sequenceDiagram
    participant Vendor as Vendor Control Panel
    participant n8n as Embedded n8n
    participant MCP as MCP Server

    Vendor->>n8n: Trigger Workflow
    n8n->>MCP: Execute Action
    n8n-->>Vendor: Workflow Outcome

```
---

## 6.4 Additional Runtime Use Cases (To Be Detailed)

The following runtime scenarios are considered relevant for Sentra Brain but are outside the immediate Phase 1 implementation scope. They will be defined and documented in later iterations:

- **User Account Management:**  
  - **Scenario:** A system administrator creates, updates, or disables user accounts via the Admin Panel.  
  - **Flow:** Admin Panel → Sentra API → Auth Service.

- **CRM/ERP Integration via MCP:**  
  - **Scenario:** This use case is already documented in detail in section 6.2.2.  
  - **Reference:** See section 6.2.2 for the flow and step-by-step details.

- **License Validation and Health Monitoring:**  
  - **Scenario:** JGCarmona Consulting performs periodic service health checks and license validation remotely.  
  - **Flow:** Monitoring Client → Sentra API → Secure /health Endpoint.

**Notes:**  
- These scenarios follow the same core architecture principles: self-hosted first, vendor-managed access strictly controlled, modular service separation.
