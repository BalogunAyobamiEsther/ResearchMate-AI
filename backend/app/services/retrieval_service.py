
from backend.app.services.embedding_service import generate_embedding
from backend.app.services.vector_store import research_collection


def retrieve_relevant_chunks(
    question: str,
    owner_session_id: str,
    top_k: int = 5,
) -> list[dict]:
    """
    Retrieve relevant document chunks belonging only to a specific
    browser session and remove exact duplicates.
    """

    # Validate the session owner.
    if not owner_session_id:
        raise ValueError("A valid owner session ID is required.")

    # Remove unnecessary whitespace from the question.
    question = question.strip()

    # Validate the question.
    if not question:
        raise ValueError("The question cannot be empty.")

    # Validate the number of results.
    if top_k <= 0:
        raise ValueError("top_k must be greater than zero.")

    # Define the ownership filter.
    ownership_filter = {
        "owner_session_id": owner_session_id,
    }

    # Convert the question into an embedding.
    question_embedding = generate_embedding(question)

    # Count only chunks belonging to this session.
    session_chunks = research_collection.get(
        where=ownership_filter,
        include=["metadatas"],
    )

    total_chunks = len(session_chunks["ids"])

    # Return an empty list if this session has no documents.
    if total_chunks == 0:
        return []

    # Retrieve a larger candidate pool to allow deduplication.
    candidate_count = min(total_chunks, top_k * 3)

    # Search only this session's document chunks.
    search_results = research_collection.query(
        query_embeddings=[question_embedding],
        n_results=candidate_count,
        where=ownership_filter,
        include=["documents", "metadatas", "distances"],
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
        chunk_ids,
        documents,
        metadatas,
        distances,
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
            "distance": distance,
        })

        # Stop when we have enough unique passages.
        if len(retrieved_chunks) == top_k:
            break

    return retrieved_chunks
