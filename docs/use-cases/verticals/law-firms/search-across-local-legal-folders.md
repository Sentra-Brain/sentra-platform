# Use Case: Search Across Local Legal Folders

**Category:** Vertical — Law Firms  
**Actors:** Authenticated User (Lawyer), Sentra Brain System  
**Priority:** Medium  
**Triggers:** User submits a query related to files stored in local legal folder structures  

## Description

Law firm users can search for documents stored outside Sentra Brain’s Knowledge Base, specifically in shared folders or NAS storage configured by the organization.

Sentra Brain connects to these folders via an MCP server (e.g., sentra-crm or sentra-doc) that indexes or queries file names, metadata, and optionally file contents.

This allows maintaining flexible file structures without requiring full import into Sentra Brain’s ChromaDB.

## Basic Flow

1. Administrator configures one or more local legal folder paths via MCP server setup.
2. User logs into Sentra Web.
3. User accesses the "Local Folder Search" section or submits a chat query requesting file lookup.
4. Sentra Brain API invokes the configured MCP server:
    - Sends query parameters (e.g., keywords, date range).
5. MCP server scans folder paths:
    - Matches filenames, metadata, and optionally content previews.
6. System displays search results:
    - Filename
    - Path or location reference
    - Last modified date
    - File size
7. User downloads or previews files directly if permissions allow.

## Extensions

- If folder access is restricted:
    - System hides that path from users and informs admin.
- If MCP server detects new files:
    - Optional auto-indexing or alert generation.

## Notes

- Requires proper filesystem permissions and secure handling.
- MCP server handles folder access using static config or dynamic discovery (future feature).
- This is file-level search — deeper content indexing requires full Knowledge Base import.
- Admins must regularly maintain folder paths and access control lists.
