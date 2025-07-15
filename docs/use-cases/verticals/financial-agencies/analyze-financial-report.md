# Use Case: Analyze Financial Report

**Category:** Vertical — Financial Agencies (Tax Agencies)  
**Actors:** Authenticated User (Agent), Sentra Brain System  
**Priority:** High  
**Triggers:** User uploads a financial document or submits a related query  

## Description

Financial agency users upload or reference structured reports such as income statements, balance sheets, or tax forms.  
Sentra Brain summarizes key figures, highlights discrepancies, and optionally suggests observations using LLM and RAG capabilities.

This reduces the time spent manually reviewing client-submitted reports.

## Basic Flow

1. User logs into Sentra Web.
2. User navigates to the Financial Reports section.
3. User uploads a document or pastes structured data.
4. Sentra Brain API processes the document:
    - Extracts key financial figures.
    - Optionally references past reports or Knowledge Base content.
5. User requests an analysis or summary.
6. Sentra Brain forwards the structured data and context to the LLM backend.
7. System presents:
    - Key figure summary.
    - Possible issues detected (e.g., inconsistent revenue declarations).
    - Suggested next actions (review thresholds, client contact, etc.).

## Extensions

- If OCR is required (scanned PDFs):
    - System queues the document for pre-processing (future phase).
- If the document is linked to a specific client:
    - System cross-references client profile (licensed versions only).

## Notes

- Designed for structured document types:  
    - Quarterly reports, Modelo 303, Modelo 130, VAT declarations, etc.  
- Document processing is confidential and never shared across organizations.
- Admins can configure threshold alerts and reporting preferences.
