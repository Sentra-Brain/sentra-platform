# Use Case: Lookup Compliance Regulation

**Category:** Vertical — Financial Agencies (Tax Agencies)  
**Actors:** Authenticated User (Agent), Sentra Brain System  
**Priority:** High  
**Triggers:** User submits a query about legal, tax, or financial regulations  

## Description

Financial agency users often need quick access to up-to-date compliance rules and regulations, including tax deadlines, fiscal regimes, and accounting standards.  
Sentra Brain allows users to query compliance information either via internal Knowledge Base (RAG) or through external MCP-connected regulation databases.

This reduces dependency on manual frontends/website checks or outdated reference materials.

## Basic Flow

1. User logs into Sentra Web.
2. User opens the chat interface and selects "Knowledge Base + Tools" mode.
3. User submits a query, e.g.:
    - “What is the VAT payment deadline for Q2 2025 in Spain?”
    - “Explain Modelo 111 filing requirements.”
4. Sentra Brain API processes the query:
    - Searches ChromaDB for relevant indexed regulations.
    - If necessary, invokes an MCP server connected to external regulatory APIs or databases.
5. System presents:
    - Direct answer summary.
    - Reference links or document attachments (if available).
    - Applicable dates or forms.

## Extensions

- If compliance data is outdated:
    - Admin is notified to update the dataset.
- If the query is outside indexed topics:
    - System suggests contacting legal advisors or adds the question to a review queue.

## Notes

- Regulation datasets can be managed by the administrator and updated periodically.
- MCP servers may integrate with:
    - BOE (Boletín Oficial del Estado) APIs.
    - Hacienda or Social Security systems (subject to legal compliance).
- Answers are not legally binding and should be verified by certified professionals.
