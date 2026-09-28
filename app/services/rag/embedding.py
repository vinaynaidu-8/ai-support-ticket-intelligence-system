from typing import Any

from sentence_transformers import SentenceTransformer


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Load the embedding model once when this module is loaded.
model = SentenceTransformer(MODEL_NAME)


def embed_text(text: str) -> list[float]:
    """
    Convert a single text string into an embedding vector.
    """
    embedding = model.encode(
        text,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )

    return embedding.tolist()


def embed_chunks(chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Generate an embedding vector for every knowledge chunk.

    The original chunk text and metadata are preserved.
    """
    texts = [chunk["text"] for chunk in chunks]

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )

    embedded_chunks = []

    for chunk, embedding in zip(chunks, embeddings):
        embedded_chunks.append(
            {
                "text": chunk["text"],
                "source": chunk["source"],
                "category": chunk["category"],
                "embedding": embedding.tolist(),
            }
        )

    return embedded_chunks