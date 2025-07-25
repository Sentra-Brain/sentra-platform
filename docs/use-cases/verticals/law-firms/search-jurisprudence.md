# Use Case: Search Jurisprudence (Law Firms)

**Category:** Vertical — Law Firms  
**Actors:** Authenticated User (Lawyer), Sentra Brain System  
**Priority:** High  
**Triggers:** User submits a legal query related to jurisprudence  

## Description

Law firm users can search for legal precedents, case law, or jurisprudence records via Sentra Brain.  
This capability relies on a dedicated MCP server configured with access to local legal databases, public legal APIs, or proprietary jurisprudence datasets.  

## Basic Flow

1. User logs into Sentra Web.
2. User opens the chat interface and selects "Tools (MCP Skills)" mode.
3. User submits a query such as "Find recent Spanish Supreme Court rulings on data privacy."
4. Sentra Brain API forwards the query to the LLM backend.
5. LLM responds with a structured tool invocation targeting `search_jurisprudence`.
6. Sentra Brain API invokes the configured MCP server.
7. MCP server queries connected legal databases and returns structured results:
    - Case name
    - Court
    - Date
    - Summary
    - Reference links (if applicable)
8. Sentra Brain presents the results to the user in a clear, lawyer-friendly format.

## Extensions

- If no relevant jurisprudence is found:
    - System informs the user and suggests refining the query.
- If multiple MCP servers are configured:
    - System aggregates results from all connected jurisprudence sources.
- If the MCP server requires authentication:
    - System uses pre-configured secure tokens or keys (managed by the administrator).

## Notes

- Jurisprudence datasets can be hosted locally or accessed via secured APIs depending on jurisdictional compliance (e.g., GDPR).
- Admins can configure which MCP servers handle legal search per organization.
- Sentra Brain does not store legal query content beyond the current session unless explicitly configured.
