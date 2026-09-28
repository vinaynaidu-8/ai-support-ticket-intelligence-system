from sqlalchemy.orm import Session

from app.models.knowledge_chunk import KnowledgeChunk
from app.services.rag.embedding import embed_text
from app.services.rag.reranking import rerank


def retrieve_knowledge(
    db: Session,
    query: str,
    candidate_k: int = 10,
    final_k: int = 5,
) -> list[dict]:

    query_vector = embed_text(query)

    candidates = (
        db.query(KnowledgeChunk)
        .order_by(
            KnowledgeChunk.embedding.cosine_distance(query_vector)
        )
        .limit(candidate_k)
        .all()
    )

    return rerank(
        query=query,
        results=candidates,
        top_k=final_k,
    )