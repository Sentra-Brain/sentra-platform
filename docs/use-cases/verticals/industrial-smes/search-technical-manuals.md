# Use Case: Search Technical Manuals and Procedures

**Category:** Vertical — Industrial SMEs  
**Actors:** Authenticated User (Employee), Sentra Brain System  
**Priority:** High  
**Triggers:** User submits a query related to machinery, protocols, or processes  

## Description

Industrial SME employees often need quick access to technical manuals, safety procedures, ISO documentation, or machine-specific instructions.  
Sentra Brain allows searching across uploaded documents using RAG, improving efficiency and reducing operational downtime.

## Basic Flow

1. User logs into Sentra Web.
2. User opens the Knowledge Base search tool or chat interface.
3. User submits a query such as:
    - “Show the maintenance protocol for Machine X.”
    - “What are the ISO 9001 procedures for packaging?”
4. Sentra Brain API processes the query:
    - Searches ChromaDB for relevant indexed manuals or documents.
5. System presents:
    - Relevant excerpts.
    - Document previews.
    - Links to download full manuals.

## Extensions

- Admin periodically updates manuals and procedures via the Document Uploader.
- System can prioritize certain document types (e.g., safety over general maintenance).

## Notes

- Designed for internal use — employees access only the manuals relevant to their role.
- MCP integration optional for live data from external systems.
- This feature operates fully offline if required, ensuring privacy and compliance.
