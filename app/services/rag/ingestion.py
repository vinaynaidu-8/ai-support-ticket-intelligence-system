from pathlib import Path
from typing import Any


KNOWLEDGE_DIR = Path("knowledge")


def load_documents() -> list[dict[str, Any]]:
    """
    Load all Markdown knowledge documents.

    Returns:
        A list containing document text and basic metadata.
    """
    documents = []

    for file_path in KNOWLEDGE_DIR.rglob("*.md"):
        text = file_path.read_text(encoding="utf-8").strip()

        if not text:
            continue

        relative_path = file_path.relative_to(KNOWLEDGE_DIR)

        documents.append(
            {
                "text": text,
                "source": str(relative_path).replace("\\", "/"),
                "category": file_path.parent.name,
            }
        )

    return documents


def chunk_document(document: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Split a Markdown document into meaningful section-based chunks.

    A heading is kept together with the content that follows it.
    A heading by itself is not treated as a separate chunk.
    """
    lines = document["text"].splitlines()

    chunks = []
    current_chunk: list[str] = []
    has_content = False

    for line in lines:
        is_heading = line.lstrip().startswith("#")

        if is_heading and has_content:
            chunk_text = "\n".join(current_chunk).strip()

            if chunk_text:
                chunks.append(
                    {
                        "text": chunk_text,
                        "source": document["source"],
                        "category": document["category"],
                    }
                )

            current_chunk = [line]
            has_content = False

        else:
            current_chunk.append(line)

            if line.strip() and not is_heading:
                has_content = True

    if current_chunk:
        chunk_text = "\n".join(current_chunk).strip()

        if chunk_text:
            chunks.append(
                {
                    "text": chunk_text,
                    "source": document["source"],
                    "category": document["category"],
                }
            )

    return chunks


def build_knowledge_chunks() -> list[dict[str, Any]]:
    """
    Load all knowledge documents and split them into chunks.
    """
    documents = load_documents()

    all_chunks = []

    for document in documents:
        chunks = chunk_document(document)
        all_chunks.extend(chunks)

    return all_chunks