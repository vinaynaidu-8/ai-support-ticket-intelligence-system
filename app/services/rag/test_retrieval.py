from sklearn.metrics.pairwise import cosine_similarity

from app.services.rag.embedding import embed_chunks, embed_text
from app.services.rag.ingestion import build_knowledge_chunks


# ---------------------------------------------------------
# 1. Build and embed the knowledge base
# ---------------------------------------------------------

chunks = build_knowledge_chunks()
embedded_chunks = embed_chunks(chunks)


# ---------------------------------------------------------
# 2. User query
# ---------------------------------------------------------

query = "Why am I receiving HTTP 401 errors when calling the API?"


# ---------------------------------------------------------
# 3. Convert the query into a vector
# ---------------------------------------------------------

query_vector = embed_text(query)


# ---------------------------------------------------------
# 4. Compare query vector against every chunk vector
# ---------------------------------------------------------

results = []

for chunk in embedded_chunks:
    similarity = cosine_similarity(
        [query_vector],
        [chunk["embedding"]],
    )[0][0]

    results.append(
        {
            "similarity": float(similarity),
            "text": chunk["text"],
            "source": chunk["source"],
            "category": chunk["category"],
        }
    )


# ---------------------------------------------------------
# 5. Rank by similarity
# ---------------------------------------------------------

results.sort(
    key=lambda result: result["similarity"],
    reverse=True,
)


# ---------------------------------------------------------
# 6. Display top results
# ---------------------------------------------------------

print("\nQuery:")
print(query)

print("\nTop relevant chunks:\n")

for rank, result in enumerate(results[:5], start=1):
    print("=" * 70)
    print(f"Rank: {rank}")
    print(f"Similarity: {result['similarity']:.4f}")
    print(f"Source: {result['source']}")
    print(f"Category: {result['category']}")
    print("-" * 70)
    print(result["text"])