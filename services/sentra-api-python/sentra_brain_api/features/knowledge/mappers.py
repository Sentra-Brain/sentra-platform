# sentra_brain_api/features/knowledge/mappers.py

from sentra.domain.entities.document_entity import DocumentEntity
from sentra.domain.entities.knowledge_source_entity import KnowledgeSourceEntity
from sentra_brain_api.features.knowledge.schemas import DocumentResponse, KnowledgeSourceResponse
from sentra_brain_api.shared_models.user_refs import UserRef

def to_document_response(entity: DocumentEntity) -> DocumentResponse:
    return DocumentResponse(
        id=entity.id,
        filename=entity.filename,
        display_name=entity.display_name,
        description=entity.description,
        filetype=entity.filetype,
        path=entity.path,
        created_by=UserRef.from_orm(entity.created_by),
        created_at=entity.created_at,
        status=entity.status,
        status_message=entity.status_message,
        error=entity.error,
        chunks_count=entity.chunks_count,
        knowledge_source_id=entity.knowledge_source_id,
        has_markdown=entity.has_markdown,
    )

def to_knowledge_source_response(entity: KnowledgeSourceEntity) -> KnowledgeSourceResponse:
    return KnowledgeSourceResponse(
        id=entity.id,
        name=entity.name,
        type=entity.type,
        path=entity.path,
        description=entity.description,
        created_by=UserRef.from_orm(entity.created_by),
        created_at=entity.created_at,
        visibility=entity.visibility,
        auto_index=entity.auto_index,
        status=entity.status
    )
