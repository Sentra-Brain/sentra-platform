# Use Case: Search Previous Case Studies

**Category:** Vertical — Healthcare  
**Actors:** Authenticated User (Doctor, Researcher), Sentra Brain System  
**Priority:** Medium to High  
**Triggers:** User submits a query about previous patient cases or research topics  

## Description

Doctors and medical researchers can query Sentra Brain to search across anonymized internal case studies, research papers, and clinical trials stored locally.  
This supports clinical decision-making and continuous medical education.

## Basic Flow

1. User logs into Sentra Web.
2. User opens the Case Studies search or chat interface.
3. User submits a query such as:
    - “Cases of Type 2 Diabetes with atypical symptoms.”
    - “Research on post-COVID lung function.”
4. Sentra Brain searches ChromaDB for relevant documents.
5. System displays:
    - Relevant case study summaries.
    - Reference links or document downloads.
    - Citation details.

## Extensions

- Admin curates and updates the case study dataset regularly.
- Access control: only authorized users (e.g., doctors, researchers) can query this data.

## Notes

- Anonymization must comply with GDPR, HIPAA, and local regulations.
- Does not replace certified medical databases but enhances internal knowledge sharing.
