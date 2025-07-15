# Use Case: Lookup Legal Representation Requirements

**Category:** Vertical — Financial Agencies (Tax Agencies)  
**Actors:** Authenticated User (Agent), Sentra Brain System  
**Priority:** Low to Medium  
**Triggers:** User submits a query about legal representation before public administration  

## Description

Financial agency users can check which documents and legal steps are required to represent a client before different government bodies (Agencia Tributaria, Seguridad Social, etc.).  
Sentra Brain provides up-to-date guidance based on indexed regulations or MCP integration with external legal sources.

## Basic Flow

1. User logs into Sentra Web.
2. User opens the chat interface or Representation Requirements page.
3. User submits a query such as:
    - “What’s required to represent a client before the Agencia Tributaria?”
    - “Do I need a power of attorney for Seguridad Social procedures?”
4. Sentra Brain processes the query:
    - Searches ChromaDB for relevant regulations and procedure guides.
    - Optionally calls MCP servers connected to public legal information databases.
5. System displays:
    - Required authorizations (e.g., apoderamiento, notarial acts).
    - Form templates (if applicable).
    - Reference laws and official instructions.

## Extensions

- Admin updates internal content when new requirements are published.
- MCP integration with public administration systems (future feature) for real-time validation.

## Notes

- Legal responsibility always remains with the certified gestoría or legal representative.
- The system helps avoid common mistakes by providing clear procedural checklists.
- Information can be filtered by government body and procedure type.
