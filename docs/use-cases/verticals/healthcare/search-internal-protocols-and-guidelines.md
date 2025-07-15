# Use Case: Search Internal Protocols and Guidelines

**Category:** Vertical — Healthcare  
**Actors:** Authenticated User (Healthcare Staff), Sentra Brain System  
**Priority:** High  
**Triggers:** User submits a query related to treatment protocols or internal rules  

## Description

Sentra Brain allows healthcare staff to search across indexed internal treatment protocols, administrative guidelines, and best practice documents using RAG technology.

This supports faster, more accurate decisions in patient care and administration.

## Basic Flow

1. User logs into Sentra Web.
2. User opens the Knowledge Base search or chat interface.
3. User submits a query such as:
    - “COVID-19 isolation protocol.”
    - “Procedure for MRI patient preparation.”
4. Sentra Brain searches ChromaDB for relevant indexed documents.
5. System displays:
    - Relevant excerpts.
    - Document links.
    - Reference dates and authors.

## Extensions

- Admin uploads new or updated protocols via Sentra Admin.
- Access restrictions per user role (doctor, nurse, admin staff).

## Notes

- Operates fully offline for privacy-compliant deployments.
- Reduces dependency on outdated printed manuals.
- Protocol update alerts can be configured (future feature).
