# Use Case: Internet Search Tool (MCP Skill)

**Category:** Core  
**Actors:** Authenticated User, Sentra Brain System  
**Priority:** Medium (optional feature)  
**Triggers:** User sends a chat message requiring external information  

## Description

Sentra Brain allows users to request real-time information retrieval from public internet sources through a dedicated MCP server (sentra-search).

This tool complements the local Knowledge Base by fetching up-to-date content when appropriate.

## Basic Flow

1. User logs into Sentra Web.
2. User opens the chat interface and selects "Tools (MCP Skills)" mode.
3. User types a question that cannot be answered with local context (e.g., "What's the latest court ruling on X?").
4. Sentra Brain API forwards the message to the LLM backend.
5. LLM issues a structured tool call requesting internet search.
6. Sentra Brain API invokes the sentra-search MCP server.
7. MCP server queries public internet sources (search engines, APIs, or RSS feeds).
8. Sentra Brain receives and optionally summarizes the results.
9. LLM continues the conversation including the retrieved information.

## Extensions

- If internet access is restricted (offline deployment):
    - System disables this skill or shows a warning to the user.
- If the MCP server returns too many or no results:
    - System adjusts the query or informs the user.

## Notes

- Internet search must comply with privacy and security policies defined per installation.
- Admins can enable or disable this feature via MCP server management.
- Results may be cached temporarily to reduce repeated external calls.
