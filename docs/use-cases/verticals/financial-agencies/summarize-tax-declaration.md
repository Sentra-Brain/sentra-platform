# Use Case: Summarize Tax Declaration

**Category:** Vertical — Financial Agencies (Tax Agencies)  
**Actors:** Authenticated User (Agent), Sentra Brain System  
**Priority:** High  
**Triggers:** User uploads a tax declaration file or requests a summary  

## Description

Financial agency users frequently handle tax declaration forms such as Modelo 303, Modelo 130, or annual declarations.  
Sentra Brain allows users to upload these documents or paste structured data, automatically generating summaries that highlight key figures, filing dates, and anomalies.

This streamlines repetitive checks and improves accuracy during tax periods.

## Basic Flow

1. User logs into Sentra Web.
2. User accesses the Tax Declarations section.
3. User uploads a declaration file (PDF, XML, DOCX) or pastes form data.
4. Sentra Brain API processes the document:
    - Extracts structured fields.
    - Cross-references known tax form formats.
    - Highlights totals, due amounts, deductions, and critical dates.
5. User clicks "Summarize".
6. Sentra Brain sends the structured information to the LLM backend for summarization.
7. System presents:
    - Summary report.
    - Key amounts (VAT owed, retained amounts, etc.).
    - Filing status reminders.

## Extensions

- If file format is unknown:
    - System suggests manual review.
- If filing deadline is approaching:
    - System shows an alert or calendar reminder (future feature).

## Notes

- Document parsing must comply with GDPR and organizational privacy requirements.
- Templates for common Spanish forms like Modelo 303, 111, 130 should be preloaded in the system.
- This feature complements, but does not replace, certified accounting software.
