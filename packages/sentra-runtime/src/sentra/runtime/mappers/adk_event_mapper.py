from uuid import UUID, uuid4
from google.adk.events import Event as ADKEvent
from sentra.domain.models.event import SentraEvent, SentraEventContent, SentraEventContentPart

def from_adk(event: ADKEvent) -> SentraEvent:
    return SentraEvent(
        id=UUID(event.id) if event.id else uuid4(),
        invocation_id=UUID(event.invocation_id) if getattr(event, 'invocation_id', None) else None,
        timestamp=event.timestamp,
        author=event.author,
        type=event.type,
        partial=getattr(event, "partial", None),
        turn_complete=getattr(event, "turn_complete", None),
        content=SentraEventContent(
            role=getattr(event.content, "role", None),
            parts=[SentraEventContentPart(text=p.text) for p in getattr(event.content, "parts", []) if hasattr(p, "text")]
        ) if getattr(event, 'content', None) else None,
        meta=getattr(event, "metadata", {}),
    )

def to_adk(event: SentraEvent) -> ADKEvent:
    return ADKEvent(
        id=str(event.id),
        invocation_id=str(event.invocation_id) if event.invocation_id else None,
        timestamp=event.timestamp.timestamp(),
        author=event.author,
        type=event.type,
        # Map content parts if needed...
    )
