# Use Case: Summarize Medical Report

**Category:** Vertical — Healthcare  
**Actors:** Authenticated User (Doctor, Nurse), Sentra Brain System  
**Priority:** High  
**Triggers:** User uploads or pastes a medical report for summarization  

## Description

Healthcare professionals can upload or paste patient medical reports (clinical histories, lab results, specialist notes) and receive a structured summary highlighting diagnoses, treatments, and relevant observations.

This saves time during consultations while ensuring sensitive data remains on-premises.

## Basic Flow

1. User logs into Sentra Web.
2. User accesses the “Medical Reports” section.
3. User uploads or pastes a medical report.
4. Sentra Brain processes the content:
    - Detects key sections (diagnosis, treatment, lab values).
    - Generates an executive summary.
5. System displays:
    - Key patient information.
    - Diagnoses.
    - Suggested next actions or flagged alerts.
6. User can download the summary or copy it into patient records.

## Extensions

- Admin can configure summarization styles: short, detailed, clinical focus.
- Integration with hospital information systems (future phase).

## Notes

- Compliant with GDPR, HIPAA, and local privacy regulations.
- No external API calls unless explicitly configured through MCP servers.
- Supports multi-language reports depending on the LLM model used.
