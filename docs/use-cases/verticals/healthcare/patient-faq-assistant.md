# Use Case: Patient FAQ Assistant

**Category:** Vertical — Healthcare  
**Actors:** Authenticated User (Reception Staff, Admin Staff), Sentra Brain System  
**Priority:** Medium  
**Triggers:** User submits a query related to administrative or non-clinical topics  

## Description

Sentra Brain provides healthcare staff with instant answers to frequently asked patient questions regarding administrative processes, facility hours, billing, or general preparation instructions.  
This helps non-medical personnel provide consistent information without consulting multiple internal sources.

## Basic Flow

1. Reception or admin staff logs into Sentra Web.
2. User opens the FAQ Assistant chat interface.
3. User submits a question such as:
    - “When are visiting hours?”
    - “What’s required for MRI preparation?”
    - “Where can I pay the hospital bill?”
4. Sentra Brain searches ChromaDB for relevant indexed documents and FAQs.
5. System displays:
    - Short, direct answers.
    - Reference documents or links.
    - Suggested actions if necessary.

## Extensions

- Admin uploads or updates FAQ content via Sentra Admin UI.
- Multilingual support for international patient contexts.

## Notes

- No sensitive patient data involved.
- Strictly administrative: does not answer medical diagnosis or treatment questions.
