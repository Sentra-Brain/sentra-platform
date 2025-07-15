# Use Case: Chat with LLM (Plain)

**Category:** Core  
**Actors:** Authenticated User, Sentra Brain System  
**Priority:** High  
**Triggers:** User sends a chat message  

## Description

The user initiates a chat session through Sentra Web. Sentra Brain forwards the user message directly to the configured LLM backend without additional context or external tool invocation.

This is the simplest interaction flow, used as the fallback when RAG or MCP skills are not selected or not available.

## Basic Flow

1. User logs into Sentra Web.
2. User accesses the chat interface.
3. User types a message and sends it.
4. Sentra Brain API authenticates the request and verifies slot availability.
5. Sentra Brain forwards the message to the configured LLM backend (llama.cpp, OpenAI, etc.).
6. The LLM responds with the generated output.
7. Sentra Brain API relays the response back to the frontend.
8. The frontend displays the response to the user.

## Extensions

- If the user exceeds allowed rate limits → System displays an error.
- If the LLM backend is unavailable → System shows fallback message or error.

## Notes

- This use case does not include RAG or MCP interactions.
- Message history may be included in the payload, respecting LLM context window limits.
- Frontend must display connection status and response loading indicators.
