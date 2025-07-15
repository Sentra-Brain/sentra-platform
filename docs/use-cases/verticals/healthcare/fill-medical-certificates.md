# Use Case: Fill Medical Certificates Automatically

**Category:** Vertical — Healthcare  
**Actors:** Authenticated User (Doctor, Nurse), Sentra Brain System  
**Priority:** Medium  
**Triggers:** User requests help filling a medical certificate  

## Description

Healthcare professionals frequently issue certificates such as sick leave notes, fitness-for-work reports, and discharge summaries.  
Sentra Brain helps generate pre-filled certificate drafts based on minimal input, reducing repetitive form filling tasks.

## Basic Flow

1. User logs into Sentra Web.
2. User opens the “Medical Certificates” tool.
3. User selects certificate type:
    - Sick leave note
    - Fitness-for-work report
    - Hospital discharge summary
4. User provides key patient information:
    - Name, ID
    - Dates
    - Diagnosis (optional)
5. Sentra Brain generates a draft certificate.
6. User reviews, edits if necessary, and downloads the document.

## Extensions

- MCP integration with hospital systems to auto-fill patient data.
- Admin UI for managing certificate templates.

## Notes

- Drafts are not legally valid until reviewed and signed by a certified medical professional.
- Operates fully offline if required.
