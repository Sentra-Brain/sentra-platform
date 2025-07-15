# Use Case: Precedent Similarity Search (Law Firms)

**Category:** Vertical — Law Firms  
**Actors:** Authenticated User (Lawyer), Sentra Brain System  
**Priority:** Medium to High  
**Triggers:** User submits a fact pattern or case description  

## Description

Law firm users can search for precedent cases that are similar in fact pattern, not just by keyword.  
Sentra Brain uses ChromaDB and embedding-based similarity search across indexed jurisprudence records or case law databases.

This helps legal professionals discover relevant precedents more efficiently, beyond traditional keyword search methods.

## Basic Flow

1. User logs into Sentra Web.
2. User opens the chat interface or a dedicated “Precedent Search” page.
3. User submits a natural language description of a case scenario or fact pattern.
4. Sentra Brain generates embeddings for the user’s input.
5. Sentra Brain queries ChromaDB against indexed case law embeddings.
6. System returns a ranked list of similar precedents:
    - Case name
    - Court
    - Date
    - Similarity score
    - Key excerpts or summaries

## Extensions

- If the database is too large:
    - System limits queries to recent years or specific courts.
- If similarity scores are too low:
    - System suggests refining the query or adding more context.
- Optional: User can select filters like jurisdiction, case type, date range.

## Notes

- Requires a properly indexed and pre-processed jurisprudence dataset stored in ChromaDB.
- Does not replace formal legal research but accelerates the first screening.
- Admins configure dataset sources and indexing frequency.
- This feature may be disabled in offline or restricted deployments if external case law access is not available.
