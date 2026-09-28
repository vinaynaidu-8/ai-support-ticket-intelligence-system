from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.models.knowledge_chunk import KnowledgeChunk
from app.services.rag.embedding import embed_text


def search_knowledge(
    db: Session,
    query: str,
    top_k: int = 5,
) -> list[KnowledgeChunk]:

    query_vector = embed_text(query)

    results = (
        db.query(KnowledgeChunk)
        .order_by(
            KnowledgeChunk.embedding.cosine_distance(query_vector)
        )
        .limit(top_k)
        .all()
    )

    return results


if __name__ == "__main__":
    query = "Why am I receiving HTTP 401 errors when calling the API?"

    db = SessionLocal()

    try:
        results = search_knowledge(
            db=db,
            query=query,
            top_k=5,
        )

        print("\nQuery:")
        print(query)

        print("\nTop PostgreSQL vector-search results:\n")

        for rank, result in enumerate(results, start=1):
            print("=" * 70)
            print(f"Rank: {rank}")
            print(f"Source: {result.source}")
            print(f"Category: {result.category}")
            print("-" * 70)
            print(result.content)

    finally:
        db.close()