# Use Case: Generate Meeting Minutes Summary (City Hall)

**Category:** Vertical — Public Sector  
**Actors:** Authenticated User (Public Agent), Sentra Brain System  
**Priority:** Medium  
**Triggers:** User uploads or pastes meeting transcript or notes  

## Description

Sentra Brain allows public agents to automatically summarize meeting transcripts, council sessions, or administrative meetings.  
The summary can include key decisions, assigned actions, and attendance records, reducing manual documentation time.

## Basic Flow

1. User logs into Sentra Web.
2. User uploads a meeting transcript file or pastes notes.
3. User clicks “Generate Summary.”
4. Sentra Brain processes the content using LLM summarization.
5. System displays:
    - Summary report
    - Action points list
    - Downloadable PDF/DOCX file

## Extensions

- Integration with the city hall document management system (via MCP).
- Multi-language summarization (Spanish, Catalan, etc.).

## Notes

- Designed for internal use: draft minutes may require human review before publication.
- Summarization settings (detail level, sectioning) can be configured by administrators.
