# Use Case: Customer Support FAQ Assistant

**Category:** Vertical — Industrial SMEs  
**Actors:** Authenticated User (Support Agent), Sentra Brain System  
**Priority:** Medium  
**Triggers:** User submits a query related to product troubleshooting or FAQs  

## Description

Industrial SME support staff can query Sentra Brain for pre-indexed product FAQs, troubleshooting guides, and compatibility information to assist customers more efficiently.  
This reduces time spent searching through manuals or CRM systems manually.

## Basic Flow

1. Support Agent logs into Sentra Web.
2. Agent opens the Customer Support Assistant tool.
3. Agent submits a query such as:
    - “What is the maximum operating temperature for Product X?”
    - “How to reset Machine Y after a jam?”
4. Sentra Brain processes the query:
    - Searches ChromaDB for relevant indexed support documents or FAQs.
    - Optionally invokes an MCP server linked to the CRM.
5. System presents:
    - Direct answer or summary.
    - Reference documents or links.
    - Suggested next actions (e.g., escalate to human support).

## Extensions

- Agents can submit new FAQs for admin review and indexing.
- MCP integration with CRM allows combining static content and live ticket data.

## Notes

- Designed for internal use — end customers do not interact directly with Sentra Brain.
- Helps maintain knowledge consistency across support agents.
