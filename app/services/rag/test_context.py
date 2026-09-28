from app.database.connection import SessionLocal
from app.services.rag.context import build_context
from app.services.rag.search import retrieve_knowledge


query = "Why am I receiving HTTP 401 errors when calling the API?"

db = SessionLocal()

try:
    results = retrieve_knowledge(
        db=db,
        query=query,
        candidate_k=10,
        final_k=5,
    )

    context = build_context(results)

    print("\n" + "=" * 80)
    print("RAG CONTEXT")
    print("=" * 80)
    print(context)

finally:
    db.close()