# Use Case: Lookup Medicine Interactions

**Category:** Vertical — Healthcare  
**Actors:** Authenticated User (Doctor, Pharmacist), Sentra Brain System  
**Priority:** High  
**Triggers:** User submits a query about medication interactions  

## Description

Doctors and pharmacists use Sentra Brain to check for potential interactions between medications, using a local Knowledge Base or securely connected external databases via MCP.

This helps prevent prescription errors and ensures patient safety.

## Basic Flow

1. User logs into Sentra Web.
2. User opens the “Medication Tools” section or chat interface.
3. User submits a query such as:
    - “Interaction between Ibuprofen and Warfarin.”
    - “Can I prescribe Drug X with Drug Y?”
4. Sentra Brain processes the query:
    - Searches local medicine interaction datasets (RAG).
    - Optionally invokes an MCP server connected to external drug databases.
5. System displays:
    - Interaction warnings.
    - Pharmacological explanations.
    - Suggested alternatives or precautions.

## Extensions

- Admin manages dataset updates.
- Alert system for high-risk interactions.

## Notes

- No patient data is transmitted outside the system.
- Complements but does not replace certified pharmacological software.
- System designed to integrate with internal hospital tools via MCP when necessary.
