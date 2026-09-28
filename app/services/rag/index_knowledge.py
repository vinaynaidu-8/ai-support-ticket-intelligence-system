from app.database.connection import SessionLocal
from app.models.knowledge_chunk import KnowledgeChunk
from app.services.rag.embedding import embed_chunks
from app.services.rag.ingestion import build_knowledge_chunks


def index_knowledge_base() -> None:
    print("Loading knowledge documents...")

    chunks = build_knowledge_chunks()

    print(f"Total chunks loaded: {len(chunks)}")

    if not chunks:
        print("No knowledge chunks found.")
        return

    print("Generating embeddings...")

    embedded_chunks = embed_chunks(chunks)

    print(f"Generated embeddings: {len(embedded_chunks)}")

    db = SessionLocal()

    try:
        print("Clearing existing knowledge vector records...")

        db.query(KnowledgeChunk).delete(
            synchronize_session=False
        )

        records = []

        for chunk in embedded_chunks:
            record = KnowledgeChunk(
                content=chunk["text"],
                source=chunk["source"],
                category=chunk["category"],
                embedding=chunk["embedding"],
            )

            records.append(record)

        db.add_all(records)
        db.commit()

        print(
            f"Successfully indexed {len(records)} "
            "knowledge chunks into PostgreSQL."
        )

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    index_knowledge_base()