
from pathlib import Path
from typing import Any


# Resolve the project root independently of the terminal's working directory.
PROJECT_ROOT = Path(__file__).resolve().parents[3]

KNOWLEDGE_BASE_DIR = PROJECT_ROOT / "knowledge_base"


def load_markdown_documents() -> list[dict[str, Any]]:
    """
    Load all Markdown documents from the knowledge base.

    Returns:
        A list containing each document's filename, category,
        source path and text content.
    """

    documents = []

    if not KNOWLEDGE_BASE_DIR.exists():
        raise FileNotFoundError(
            f"Knowledge base directory not found: {KNOWLEDGE_BASE_DIR}"
        )

    for file_path in KNOWLEDGE_BASE_DIR.rglob("*.md"):

        content = file_path.read_text(encoding="utf-8").strip()

        if not content:
            continue

        category = file_path.parent.name

        documents.append(
            {
                "document_id": file_path.stem,
                "filename": file_path.name,
                "category": category,
                "source": file_path.relative_to(PROJECT_ROOT).as_posix(),
                "content": content,
            }
        )

    return documents


if __name__ == "__main__":

    loaded_documents = load_markdown_documents()

    print(f"Documents loaded: {len(loaded_documents)}")

    for document in loaded_documents:
        print("\n" + "=" * 60)
        print(f"Document: {document['filename']}")
        print(f"Category: {document['category']}")
        print(f"Source: {document['source']}")
        print(f"Characters: {len(document['content'])}")
