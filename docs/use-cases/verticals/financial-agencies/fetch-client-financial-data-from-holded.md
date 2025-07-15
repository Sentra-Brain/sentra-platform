# Use Case: Fetch Client Financial Data from Holded

**Category:** Vertical — Financial Agencies (Tax Agencies)  
**Actors:** Authenticated User (Agent), Sentra Brain System, MCP Server (Holded Connector)  
**Priority:** Medium  
**Triggers:** User submits a query about client financial data  

## Description

Financial agency users can retrieve up-to-date financial information about a client directly from Holded (or similar ERP platforms) through Sentra Brain.  
This is handled via an MCP server configured to interact with Holded’s public API.

Typical queries include checking open invoices, payment status, revenue summaries, or client balance.

## Basic Flow

1. Administrator configures MCP Server with Holded API credentials (token, company ID).
2. User logs into Sentra Web.
3. User opens the chat interface or a specific Financial Tools page.
4. User submits a query such as:
    - “What’s the outstanding balance for Cliente XYZ?”
    - “List unpaid invoices for March 2025 for Cliente XYZ.”
5. Sentra Brain API detects the request requires Holded data via MCP skill.
6. Sentra Brain API invokes the MCP Server (sentra-crm or sentra-action) with the request.
7. MCP Server calls Holded API using secure credentials.
8. MCP Server receives, formats, and returns structured JSON with:
    - Invoice lists
    - Payment status
    - Client account summaries
9. Sentra Brain injects the result into the chat response or displays it in the dedicated UI section.

## Extensions

- If the Holded API is unavailable:
    - System shows an error message and suggests retrying later.
- If multiple ERP systems are configured:
    - System prioritizes or allows user/admin to select the preferred source.

## Notes

- MCP Server acts as a secure proxy — Sentra Brain never stores Holded credentials directly.
- Admin UI must allow managing:
    - Holded API tokens
    - Company profiles
- Similar flows apply to other ERP/CRM systems (Sage, Quipu, A3, etc.) by reusing the MCP server pattern.
- Rate limiting and pagination must be handled by the MCP Server logic when dealing with large datasets.
