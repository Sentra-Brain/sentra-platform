# Use Case: Lookup Municipal Regulations

**Category:** Vertical — Public Sector  
**Actors:** Authenticated User (Public Agent), Sentra Brain System  
**Priority:** High  
**Triggers:** User submits a query about city or municipal regulations  

## Description

Public agents can query Sentra Brain for local regulations, municipal bylaws, or administrative rules.  
Sentra Brain searches the Knowledge Base (RAG) and optionally connects to official databases via MCP.

## Basic Flow

1. User logs into Sentra Web.
2. User opens the Regulations Lookup tool or uses chat.
3. User submits a query such as:
    - “What are the noise control regulations in Madrid?”
    - “Parking rules for commercial vehicles.”
4. Sentra Brain searches ChromaDB and/or MCP servers.
5. System displays:
    - Regulation summary.
    - Reference articles.
    - Downloadable regulation PDFs.

## Extensions

- Regular regulation updates via admin UI.
- MCP integration with BOE or local legislative APIs.

## Notes

- Only authorized users can access sensitive or restricted regulation documents.
- Designed as a support tool — final legal validation remains human responsibility.
