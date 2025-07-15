# Use Case: Manage MCP Server Connections

**Category:** Core  
**Actors:** Administrator, Sentra Brain System  
**Priority:** High  
**Triggers:** Administrator adds, edits, or removes MCP servers through Sentra Admin  

## Description

Administrators can configure which MCP servers are available to Sentra Brain. MCP servers provide external tools (skills) usable during chat sessions.  
Each MCP server is identified by a unique name, URL, and secret key. Connections can be tested and enabled or disabled via the Admin UI.

## Basic Flow

1. Administrator logs into Sentra Admin.
2. Administrator navigates to the MCP Server Management section.
3. The system displays the list of configured MCP servers with status indicators (online/offline, enabled/disabled).
4. Administrator adds a new MCP server:
    - Enters server name, URL, secret key.
    - System stores the configuration.
    - System optionally performs a connection test and displays the result.
5. Administrator edits an existing MCP server:
    - Updates URL or secret key.
    - System updates configuration and refreshes connection status.
6. Administrator enables or disables an MCP server:
    - System updates the active MCP Client registry in Sentra Brain API.
7. Administrator deletes an MCP server:
    - System removes configuration from storage.
    - System updates MCP Client connections.

## Extensions

- If connection test fails:
    - System shows a warning but allows saving (useful for pre-configured offline servers).
- If multiple MCP servers provide overlapping tools:
    - System aggregates tool lists but shows duplicate warnings.

## Notes

- MCP server configurations are stored securely in db-auth-users or equivalent system database.
- Sentra Brain API refreshes MCP Client connections dynamically without requiring a full restart.
- Admin UI displays server status using periodic health checks or on-demand validation.
- In licensed versions, organizations may have limits on the number of active MCP servers.
