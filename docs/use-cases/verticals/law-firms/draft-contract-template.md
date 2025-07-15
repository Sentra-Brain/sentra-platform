# Use Case: Draft Contract Template (Law Firms)

**Category:** Vertical — Law Firms  
**Actors:** Authenticated User (Lawyer), Sentra Brain System  
**Priority:** High  
**Triggers:** User requests a contract draft via chat  

## Description

Law firm users can request the generation of a contract draft using Sentra Brain.  
This use case combines LLM generation with RAG context injection from existing templates or legal clauses stored in the Knowledge Base.

The generated contract serves as a first draft, requiring review and adjustment by a legal professional.

## Basic Flow

1. User logs into Sentra Web.
2. User opens the chat interface and selects "Knowledge Base + Tools" mode.
3. User submits a prompt such as:  
   “Draft a service agreement between a software provider and a client, under Spanish law.”
4. Sentra Brain API receives the request:
    - Queries ChromaDB for relevant clauses or templates.
    - Injects those into the LLM prompt.
5. Sentra Brain forwards the enriched prompt to the LLM backend.
6. LLM generates a complete or partial contract draft.
7. System sends the generated text back to the frontend.
8. User can:
    - Copy the draft.
    - Request refinements via chat (e.g., "Make it simpler" or "Add GDPR clause").
    - Save the draft in the Knowledge Base (future phase).

## Extensions

- If no relevant templates exist in ChromaDB:
    - System warns the user and proceeds with LLM-only generation.
- If token limits are exceeded:
    - System breaks generation into sections (e.g., introduction, clauses, signatures).

## Notes

- Sentra Brain does not guarantee legal validity of generated drafts.
- Admins can manage which datasets are prioritized for RAG context in contract generation.
- Optional: Support for multilingual drafting depending on LLM model capabilities.
