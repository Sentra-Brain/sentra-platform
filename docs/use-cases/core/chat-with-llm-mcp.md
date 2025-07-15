# Use Case: Chat with LLM + Tools (MCP Skills)

**Category:** Core  
**Actors:** Authenticated User, Sentra Brain System  
**Priority:** High  
**Triggers:** User sends a chat message with Tools (MCP Skills) enabled  

## Description

When this mode is active, Sentra Brain enriches chat interactions by allowing the LLM to invoke external tools exposed via MCP (Model Context Protocol) servers. This allows dynamic workflows such as querying CRMs, sending emails, or retrieving data from internal systems.

The system manages tool discovery, invocation, and user consent flows automatically.

## Basic Flow

1. User logs into Sentra Web.
2. User opens the chat interface and selects "Tools (MCP Skills)" mode.
3. User types a message and sends it.
4. Sentra Brain API receives the message:
    - Verifies authentication and slot availability.
    - Passes the message, tool list, and context to the LLM backend.
5. LLM responds with either:
    - Plain chat response, or
    - A structured tool call (e.g., `function_call` JSON block).
6. Sentra Brain API parses tool call requests.
7. If user confirmation is required (e.g., sensitive action):
    - System prompts the user via the frontend.
    - Waits for user approval.
8. Sentra Brain API executes the MCP request using the MCP Client:
    - Sends request to the relevant MCP Server.
    - Receives tool output.
9. System sends tool output back to the LLM as part of the ongoing chat context (if required).
10. Final LLM response is relayed to the frontend.

## Extensions

- If the MCP Server is unavailable:
    - System skips tool invocation and informs the user.
- If user rejects a tool action:
    - System cancels that invocation and informs the LLM (via special context message).
- If tool execution produces an error:
    - System displays an error message to the user and optionally logs the event.

## Notes

- Available MCP servers and skills are defined per organization via Admin UI.
- MCP tool schema follows the standard MCP JSON-RPC structure.
- Sentra Brain may cache MCP server capability lists for performance.
- Admin can enable or disable specific tools per installation.
- Frontend UI must support displaying:
    - Action confirmation dialogs.
    - Execution status indicators.
    - Tool output where relevant.
