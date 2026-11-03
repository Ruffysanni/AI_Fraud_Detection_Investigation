
from typing import Any


CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150


def split_text(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> list[str]:
    """
    Divide text into overlapping chunks.

    Attempts to split at a newline or space to avoid
    breaking sentences unnecessarily.
    """

    if chunk_size <= 0:
        raise ValueError("Chunk size must be greater than zero.")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError(
            "Overlap must be non-negative and smaller than chunk size."
        )

    text = text.strip()

    if not text:
        return []

    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0

    while start < len(text):

        end = min(start + chunk_size, len(text))

        if end < len(text):
            # Look for a natural splitting point.
            newline_position = text.rfind("\n", start, end)
            space_position = text.rfind(" ", start, end)

            split_position = max(newline_position, space_position)

            # Avoid creating very small chunks.
            if split_position > start + chunk_size // 2:
                end = split_position

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        next_start = max(end - overlap, start + 1)

        # Move the next starting position to a word boundary.
        while next_start < len(text) and not text[next_start - 1].isspace():
            next_start += 1

        # Ensure the next iteration always makes progress.
        start = next_start

    return chunks


def process_documents(
    documents: list[dict[str, Any]],
    chunk_size: int = CHUNK_SIZE,
    overlap: int = CHUNK_OVERLAP,
) -> list[dict[str, Any]]:
    """
    Split loaded documents into chunks while preserving metadata.
    """

    processed_chunks = []

    for document in documents:

        chunks = split_text(
            text=document["content"],
            chunk_size=chunk_size,
            overlap=overlap,
        )

        for index, chunk in enumerate(chunks):

            processed_chunks.append(
                {
                    "chunk_id": f"{document['document_id']}_{index}",
                    "document_id": document["document_id"],
                    "filename": document["filename"],
                    "category": document["category"],
                    "source": document["source"],
                    "chunk_index": index,
                    "content": chunk,
                }
            )

    return processed_chunks


if __name__ == "__main__":

    from backend.app.rag.document_loader import load_markdown_documents

    documents = load_markdown_documents()

    chunks = process_documents(documents)

    print(f"Documents loaded: {len(documents)}")
    print(f"Total chunks created: {len(chunks)}")

    for chunk in chunks:
        print("\n" + "=" * 60)
        print(f"Chunk ID: {chunk['chunk_id']}")
        print(f"Document: {chunk['filename']}")
        print(f"Category: {chunk['category']}")
        print(f"Source: {chunk['source']}")
        print(f"Chunk index: {chunk['chunk_index']}")
        print(f"Characters: {len(chunk['content'])}")
        print(f"Content preview: {chunk['content'][:200]}...")
