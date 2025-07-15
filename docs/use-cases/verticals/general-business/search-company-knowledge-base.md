# Use Case: Search Company Knowledge Base

**Category:** Vertical — General Business  
**Actors:** Authenticated User (Employee), Sentra Brain System  
**Priority:** High  
**Triggers:** User submits a query related to internal company knowledge  

## Description

Sentra Brain allows employees to query internal guides, policies, or best practices through RAG search, reducing time spent looking for information manually.

## Basic Flow

1. User logs into Sentra Web.
2. User accesses the Knowledge Base search.
3. User submits a question, e.g.:
    - “How do I request time off?”
    - “VPN setup instructions.”
4. Sentra Brain searches ChromaDB for indexed documents.
5. System displays:
    - Direct answer.
    - Links to full documents.

## Extensions

- Admin curates Knowledge Base content.
- Access control for sensitive documents.

## Notes

- Complements existing document management tools.
