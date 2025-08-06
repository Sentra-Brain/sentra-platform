from collections import defaultdict
from typing import List
from .rag_chunk import RagChunk

def format_chunks_grouped(chunks: List[RagChunk]) -> str:
    grouped = defaultdict(lambda: defaultdict(list))  # source_id → document_id → List[chunk]

    for chunk in chunks:
        grouped[chunk.knowledge_source_id][chunk.document_id].append(chunk)

    lines = []

    for source_id, docs in grouped.items():
        lines.append(f"📁 Source `{source_id}`")
        for doc_id, doc_chunks in docs.items():
            filename = doc_chunks[0].filename or "unknown"
            lines.append(f"  📄 Document `{doc_id}` ({filename})\n")

            for chunk in doc_chunks:
                lines.append(f"    {chunk.to_prompt_block()}\n")

    return "\n".join(lines)
