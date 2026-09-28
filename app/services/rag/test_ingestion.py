from app.services.rag.ingestion import build_knowledge_chunks


chunks = build_knowledge_chunks()

print(f"\nTotal chunks: {len(chunks)}\n")

for index, chunk in enumerate(chunks, start=1):
    print("=" * 70)
    print(f"Chunk {index}")
    print(f"Source: {chunk['source']}")
    print(f"Category: {chunk['category']}")
    print("-" * 70)
    print(chunk["text"])