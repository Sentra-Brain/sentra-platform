# Use Case: Process Public Feedback Requests

**Category:** Vertical — Public Sector  
**Actors:** Authenticated User (Public Agent), Sentra Brain System, Citizen (Indirect)  
**Priority:** Medium  
**Triggers:** Incoming feedback from citizens via form, email, or messaging platform  

## Description

Sentra Brain helps city halls classify, summarize, and route citizen feedback or complaints automatically.  
This reduces manual filtering and speeds up handling minor public service issues.

## Basic Flow

1. Citizen submits feedback via a public form, email, or WhatsApp.
2. Sentra Brain receives the message through MCP Server integration.
3. System analyzes intent:
    - Complaint
    - Suggestion
    - Service request
4. System categorizes and forwards the feedback to the relevant department.
5. Optionally, Sentra Brain generates a structured report or summary.

## Extensions

- Feedback ranking by urgency or department.
- Admin can configure routing rules and categories.

## Notes

- Privacy policies apply: personal data must be handled securely.
- MCP server abstracts messaging and form channel integrations.
