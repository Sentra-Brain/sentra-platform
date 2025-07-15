# Use Case: Generate Client Invoice Summary

**Category:** Vertical — Financial Agencies (Tax Agencies)  
**Actors:** Authenticated User (Agent), Sentra Brain System  
**Priority:** Medium to High  
**Triggers:** User uploads multiple invoices or requests a client summary  

## Description

Financial agency users can request a summarized report of all invoices related to a specific client, including totals, tax breakdowns, and periods.  
This helps streamline monthly or quarterly closing processes without manual spreadsheet work.

## Basic Flow

1. User logs into Sentra Web.
2. User accesses the Invoicing or Reporting section.
3. User uploads one or more invoice files (PDF, XML, or structured JSON).
4. System processes the invoices:
    - Extracts key fields: client name, amount, VAT, date.
    - Groups invoices by client and time period (month, quarter).
5. User selects a client and time range.
6. User clicks "Generate Summary".
7. Sentra Brain API prepares:
    - Total invoiced amount.
    - Total VAT.
    - Number of invoices.
    - Summary table or downloadable report.
8. System displays or sends the report via MCP tool if configured.

## Extensions

- If client data is already linked in the system:
    - Auto-populate client selection from existing records.
- If inconsistent formats are detected:
    - System flags errors for manual correction.

## Notes

- Admins can configure accepted invoice formats and validation rules.
- MCP integration could allow automatic export to accounting software (future phase).
- This feature depends on local processing — no external APIs unless explicitly configured.
- Privacy and compliance considerations apply: invoice content is handled securely and per organization policy.
