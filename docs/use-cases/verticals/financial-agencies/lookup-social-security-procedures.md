# Use Case: Lookup Social Security Procedures

**Category:** Vertical — Financial Agencies (Tax Agencies)  
**Actors:** Authenticated User (Agent), Sentra Brain System  
**Priority:** Medium  
**Triggers:** User submits a query about social security procedures  

## Description

Allows financial agencies or labor advisors to search for official procedures, forms, and requirements related to Social Security in Spain.  
Includes processes like hiring, contract termination, worker registration, or pension applications.

## Basic Flow

1. User logs into Sentra Web.
2. User opens the chat interface or Procedure Lookup section.
3. User submits a question, e.g.:
    - “How do I register a new employee with Social Security?”
    - “Which form is required for pension application?”
4. Sentra Brain API searches ChromaDB or invokes MCP server (if configured) to retrieve:
    - Procedure description.
    - Required forms and documents.
    - Applicable deadlines and legal references.
5. System displays summarized information with reference links.

## Extensions

- If Social Security systems expose public APIs:
    - MCP server connects directly for live status checks.
- Admin updates internal procedure database regularly.

## Notes

- Focused on Spanish procedures but designed to be extendable for other countries.
- Answers serve as guidance; users are responsible for verifying final submission and legal compliance.
