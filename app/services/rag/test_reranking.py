from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.models.knowledge_chunk import KnowledgeChunk
from app.services.rag.embedding import embed_text
from app.services.rag.reranking import rerank


def search_knowledge(
    db: Session,
    query: str,
    top_k: int = 10,
) -> list[KnowledgeChunk]:

    query_vector = embed_text(query)

    return (
        db.query(KnowledgeChunk)
        .order_by(
            KnowledgeChunk.embedding.cosine_distance(query_vector)
        )
        .limit(top_k)
        .all()
    )


if __name__ == "__main__":

    query = "Why am I receiving HTTP 401 errors when calling the API?"

    db = SessionLocal()

    try:
        candidates = search_knowledge(
            db=db,
            query=query,
            top_k=10,
        )

        print("\nInitial pgvector candidates:\n")

        for rank, result in enumerate(candidates, start=1):
            print(
                f"{rank}. "
                f"{result.source} - "
                f"{result.content[:100].replace(chr(10), ' ')}"
            )

        reranked = rerank(
            query=query,
            results=candidates,
            top_k=5,
        )

        print("\n\nReranked results:\n")

        for rank, item in enumerate(reranked, start=1):

            result = item["result"]

            print("=" * 70)
            print(f"Rank: {rank}")
            print(f"Reranker score: {item['score']:.4f}")
            print(f"Source: {result.source}")
            print(f"Category: {result.category}")
            print("-" * 70)
            print(result.content)

    finally:
        db.close()