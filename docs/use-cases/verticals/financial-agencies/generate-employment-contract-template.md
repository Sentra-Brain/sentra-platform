# Use Case: Generate Employment Contract Template

**Category:** Vertical — Financial Agencies (Tax Agencies)  
**Actors:** Authenticated User (Agent), Sentra Brain System  
**Priority:** Medium  
**Triggers:** User requests to generate a contract template  

## Description

Allows financial or labor agencies to generate pre-filled employment contract templates by providing basic employee and job information.

This streamlines contract creation while ensuring legal compliance and document consistency.

## Basic Flow

1. User logs into Sentra Web.
2. User accesses the “Contract Templates” section.
3. User selects contract type (e.g., Indefinido, Temporal, Prácticas).
4. User fills in required fields:
    - Employee name
    - Start date
    - Salary details
    - Working hours
5. Sentra Brain generates a PDF or DOCX contract file based on internal templates.
6. User downloads or sends the contract directly.

## Extensions

- If regulations change:
    - Admin uploads updated contract templates.
- If employee details are incomplete:
    - System prompts user to fill missing data.

## Notes

- Templates should comply with local labor regulations.
- Final signature and submission steps happen outside Sentra Brain.
- Optionally integrates with MCP server for e-signature services (future phase).
