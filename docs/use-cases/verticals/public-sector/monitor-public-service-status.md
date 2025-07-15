# Use Case: Monitor Public Service Status

**Category:** Vertical — Public Sector  
**Actors:** Authenticated User (Public Agent), Sentra Brain System  
**Priority:** Medium to High  
**Triggers:** Regular status check requests by users or admins  

## Description

Sentra Brain helps monitor the status of public services like waste collection, traffic lights, or facility access by summarizing information from IoT dashboards, ERP systems, or MCP-integrated status APIs.

## Basic Flow

1. Admin configures MCP servers linked to public service monitoring systems.
2. Public agent logs into Sentra Web.
3. User submits a query like:
    - “Show current status of waste collection routes.”
    - “List facilities with maintenance alerts.”
4. Sentra Brain invokes MCP servers and displays:
    - Real-time status.
    - Summarized alerts.
    - Historical trends (if available).

## Extensions

- Alert generation when service thresholds are exceeded.
- Integration with public-facing dashboards.

## Notes

- Depends on existing city hall systems providing monitoring APIs.
- Designed as a backend support tool for internal public service management.
