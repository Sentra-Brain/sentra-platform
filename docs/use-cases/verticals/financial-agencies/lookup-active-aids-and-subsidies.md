# Use Case: Lookup Active Aids and Subsidies

**Category:** Vertical — Financial Agencies (Tax Agencies)  
**Actors:** Authenticated User (Agent), Sentra Brain System  
**Priority:** High  
**Triggers:** User submits a query regarding available financial aids or subsidies  

## Description

Financial agency users can query active government aids, grants, and subsidies relevant to clients (autónomos, SMEs, etc.).  
Sentra Brain retrieves this information from the internal Knowledge Base or via MCP servers connected to public databases like BOE, SEPE, or regional authorities.

## Basic Flow

1. User logs into Sentra Web.
2. User opens the chat interface or Subsidy Lookup page.
3. User submits a query such as:
    - “Show current subsidies for digitalization in Madrid.”
    - “What grants are available for new autónomos in 2025?”
4. Sentra Brain processes the query:
    - Searches ChromaDB for relevant indexed regulations and grants.
    - Optionally invokes an MCP server to fetch real-time updates.
5. System presents:
    - List of available aids and subsidies.
    - Eligibility requirements.
    - Application deadlines.
    - Links to official application portals.

## Extensions

- Admin can prioritize national vs. regional aids via configuration.
- System alerts users when new grants become available (future feature).

## Notes

- Subsidy data should be reviewed and updated periodically by administrators.
- The feature is advisory only; users must submit official applications through government portals.
- Results may vary by geographic location and client profile.
