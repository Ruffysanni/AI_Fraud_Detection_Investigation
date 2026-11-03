from typing import Any

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from backend.app.rag.document_loader import load_markdown_documents
from backend.app.rag.text_processor import process_documents


class LocalVectorStore:
    """
    Lightweight local retrieval index using TF-IDF and cosine similarity.

    This implementation uses lexical vectorization rather than
    neural-network-based semantic embeddings.
    """

    def __init__(self) -> None:
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            ngram_range=(1, 2),
        )
        self.chunks: list[dict[str, Any]] = []
        self.document_vectors = None

    def build_index(self) -> int:
        """
        Load, process and index the knowledge-base documents.

        Returns:
            Number of chunks indexed.
        """
        documents = load_markdown_documents()

        if not documents:
            raise ValueError("No documents found in the knowledge base.")

        self.chunks = process_documents(documents)

        if not self.chunks:
            raise ValueError("No text chunks were generated.")

        chunk_texts = [
            chunk["content"] for chunk in self.chunks
        ]

        self.document_vectors = self.vectorizer.fit_transform(
            chunk_texts
        )

        return len(self.chunks)

    def search(
        self,
        query: str,
        top_k: int = 3,
    ) -> list[dict[str, Any]]:
        """
        Retrieve the most relevant chunks for a search query.

        Args:
            query: User's investigation question.
            top_k: Maximum number of results to return.

        Returns:
            Ranked chunks with similarity scores and source metadata.
        """
        if self.document_vectors is None:
            raise RuntimeError(
                "The retrieval index has not been built. "
                "Call build_index() first."
            )

        if not query.strip():
            raise ValueError("Search query cannot be empty.")

        if top_k <= 0:
            raise ValueError("top_k must be greater than zero.")

        query_vector = self.vectorizer.transform([query])

        similarity_scores = cosine_similarity(
            query_vector,
            self.document_vectors,
        ).flatten()

        ranked_indices = similarity_scores.argsort()[::-1][:top_k]

        results = []

        for index in ranked_indices:
            score = float(similarity_scores[index])

            if score <= 0:
                continue

            result = self.chunks[index].copy()
            result["similarity_score"] = round(score, 4)

            results.append(result)

        return results


if __name__ == "__main__":
    vector_store = LocalVectorStore()

    total_chunks = vector_store.build_index()

    print(f"Knowledge-base chunks indexed: {total_chunks}")

    test_query = (
        "What transaction patterns could indicate suspicious "
        "movement of funds?"
    )

    search_results = vector_store.search(
        query=test_query,
        top_k=3,
    )

    print(f"\nSearch query: {test_query}")
    print(f"Results returned: {len(search_results)}")

    for result in search_results:
        print("\n" + "=" * 60)
        print(f"Chunk ID: {result['chunk_id']}")
        print(f"Document: {result['filename']}")
        print(f"Category: {result['category']}")
        print(f"Similarity score: {result['similarity_score']}")
        print(f"Source: {result['source']}")
        print(f"Content preview: {result['content'][:250]}...")