
from typing import Any

from backend.app.rag.vector_store import LocalVectorStore


class RAGRetriever:
    """
    Retrieval service that finds relevant knowledge-base chunks
    and returns their content together with source references.
    """

    def __init__(self) -> None:
        self.vector_store = LocalVectorStore()
        self.index_built = False

    def build_index(self) -> int:
        """
        Build the local retrieval index.

        Returns:
            Number of indexed knowledge-base chunks.
        """
        total_chunks = self.vector_store.build_index()
        self.index_built = True

        return total_chunks

    def retrieve(
        self,
        query: str,
        top_k: int = 3,
    ) -> dict[str, Any]:
        """
        Retrieve relevant knowledge-base information.

        Returns:
            A structured response containing the query,
            retrieved context and source references.
        """
        if not self.index_built:
            raise RuntimeError(
                "The RAG index has not been built. "
                "Call build_index() first."
            )

        if not query.strip():
            raise ValueError("Search query cannot be empty.")

        results = self.vector_store.search(
            query=query,
            top_k=top_k,
        )

        sources = []

        for result in results:
            sources.append(
                {
                    "chunk_id": result["chunk_id"],
                    "document_id": result["document_id"],
                    "filename": result["filename"],
                    "category": result["category"],
                    "source": result["source"],
                    "similarity_score": result["similarity_score"],
                }
            )

        retrieved_context = "\n\n".join(
            result["content"] for result in results
        )

        return {
            "query": query,
            "results_count": len(results),
            "retrieved_context": retrieved_context,
            "sources": sources,
        }


if __name__ == "__main__":
    retriever = RAGRetriever()

    total_chunks = retriever.build_index()

    print(f"Knowledge-base chunks indexed: {total_chunks}")

    test_query = (
        "What indicators should be investigated when "
        "a transaction rapidly moves funds out of an account?"
    )

    response = retriever.retrieve(
        query=test_query,
        top_k=3,
    )

    print("\nRAG Retrieval Results")
    print("=" * 60)

    print(f"Query: {response['query']}")
    print(f"Results count: {response['results_count']}")

    print("\nRetrieved Context:")
    print(response["retrieved_context"])

    print("\nSource References:")

    for source in response["sources"]:
        print("-" * 60)
        print(f"Chunk ID: {source['chunk_id']}")
        print(f"Document: {source['filename']}")
        print(f"Category: {source['category']}")
        print(f"Similarity: {source['similarity_score']}")
        print(f"Source: {source['source']}")
