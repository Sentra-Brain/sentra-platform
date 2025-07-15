# Use Case: Handle Internal Support Request

**Category:** Vertical — General Business  
**Actors:** Authenticated User (Employee, IT/Admin Staff), Sentra Brain System  
**Priority:** Medium  
**Triggers:** User submits a support query  

## Description

Sentra Brain assists IT and admin staff by classifying and routing internal support requests such as IT issues, facilities management, or HR questions.

## Basic Flow

1. Employee submits a request via chat or form.
2. Sentra Brain analyzes the request:
    - Classifies type (IT, HR, Facilities).
    - Extracts key details.
3. System forwards the request to the relevant team via MCP or email.
4. Optional: Sentra Brain provides immediate FAQ-style answers if available.

## Extensions

- Integration with ticketing systems (Jira, Freshdesk) via MCP.
- Request prioritization based on keywords.

## Notes

- Human validation always required before performing critical actions.
