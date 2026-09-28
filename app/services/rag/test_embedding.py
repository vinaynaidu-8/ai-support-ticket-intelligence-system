from app.services.rag.embedding import embed_chunks
from app.services.rag.ingestion import build_knowledge_chunks


chunks = build_knowledge_chunks()

embedded_chunks = embed_chunks(chunks)

print(f"\nTotal chunks: {len(embedded_chunks)}")

for index, chunk in enumerate(embedded_chunks, start=1):
    vector = chunk["embedding"]

    print("\n" + "=" * 70)
    print(f"Chunk {index}")
    print(f"Source: {chunk['source']}")
    print(f"Category: {chunk['category']}")
    print(f"Vector dimensions: {len(vector)}")
    print(f"First 5 values: {vector[:5]}")
    print("-" * 70)
    print(chunk["text"][:300])