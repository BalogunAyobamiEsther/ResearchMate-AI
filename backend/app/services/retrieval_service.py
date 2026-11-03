
from backend.app.services.embedding_service import generate_embedding
from backend.app.services.vector_store import research_collection


def retrieve_relevant_chunks(
    question: str,
    top_k: int = 5
) -> list[dict]:
    """
    Retrieve relevant document chunks and remove exact duplicates.

    Args:
        question: The user's research question.
        top_k: Maximum number of unique chunks to return.

    Returns:
        A list of relevant, unique document chunks with metadata.
    """

    # Remove unnecessary whitespace from the question.
    question = question.strip()

    # Validate the question.
    if not question:
        raise ValueError("The question cannot be empty.")

    # Validate the number of results.
    if top_k <= 0:
        raise ValueError("top_k must be greater than zero.")

    # Convert the question into an embedding.
    question_embedding = generate_embedding(question)

    # Check the number of stored chunks.
    total_chunks = research_collection.count()

    # Return an empty list if no chunks are stored.
    if total_chunks == 0:
        return []

    # Retrieve a larger candidate pool to allow deduplication.
    candidate_count = min(total_chunks, top_k * 3)

    # Search ChromaDB for the most relevant candidates.
    search_results = research_collection.query(
        query_embeddings=[question_embedding],
        n_results=candidate_count,
        include=["documents", "metadatas", "distances"]
    )

    # Extract results returned for the submitted question.
    chunk_ids = search_results["ids"][0]
    documents = search_results["documents"][0]
    metadatas = search_results["metadatas"][0]
    distances = search_results["distances"][0]

    retrieved_chunks = []
    seen_texts = set()

    # Examine candidates in relevance order.
    for chunk_id, document, metadata, distance in zip(
        chunk_ids, documents, metadatas, distances
    ):

        # Normalise text for duplicate comparison.
        normalised_text = " ".join(document.casefold().split())

        # Skip passages that have already been retrieved.
        if normalised_text in seen_texts:
            continue

        seen_texts.add(normalised_text)

        # Preserve the original passage and its metadata.
        retrieved_chunks.append({
            "chunk_id": chunk_id,
            "text": document,
            "document_id": metadata["document_id"],
            "filename": metadata["filename"],
            "page_number": metadata["page_number"],
            "distance": distance
        })

        # Stop when we have enough unique passages.
        if len(retrieved_chunks) == top_k:
            break

    return retrieved_chunks
