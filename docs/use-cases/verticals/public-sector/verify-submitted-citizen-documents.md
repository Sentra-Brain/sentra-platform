# Use Case: Verify Submitted Citizen Documents

**Category:** Vertical — Public Sector  
**Actors:** Authenticated User (Public Agent), Sentra Brain System  
**Priority:** Medium  
**Triggers:** User uploads citizen-submitted documents for validation  

## Description

City hall agents can upload citizen-submitted files (PDFs, scanned forms) and use Sentra Brain to automatically check if all required documents are present and detect missing information.

## Basic Flow

1. Public agent logs into Sentra Web.
2. Agent uploads a set of files submitted by a citizen.
3. Sentra Brain reviews:
    - File types and document names.
    - Required form presence.
    - Metadata extraction (name, ID number, date).
4. System displays:
    - Validation report.
    - List of missing or incomplete documents.
    - Suggested next steps.

## Extensions

- MCP integration with external databases to verify document authenticity (e.g., DNI, NIE validation).
- Auto-flagging duplicate submissions.

## Notes

- Final responsibility for validation rests with human agents.
- Reduces manual paperwork checking for large submission batches.
