from app.models.knowledge_chunk import KnowledgeChunk


def build_context(
    results: list[dict],
    max_chunks: int = 5,
) -> str:
    selected = results[:max_chunks]

    context_parts = []

    for index, item in enumerate(selected, start=1):
        chunk: KnowledgeChunk = item["result"]

        context_parts.append(
            f"[Knowledge Source {index}]\n"
            f"Source: {chunk.source}\n"
            f"Category: {chunk.category}\n"
            f"Content:\n{chunk.content}"
        )

    return "\n\n---\n\n".join(context_parts)
