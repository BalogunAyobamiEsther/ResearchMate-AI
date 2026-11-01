from backend.app.services.embedding_service import generate_embedding
from backend.app.services.vector_store import research_collection

def retrieve_relevant_chunks(
    question: str,
    top_k: int = 5
) -> list[dict]:
    """
    Retrieve the most relevant document chunks for a question.

    Args:
        question: The user's research question.
        top_k: Number of relevant chunks to retrieve.

    Returns:
        A list of dictionaries containing retrieved chunks
        and their metadata.
    """
        # Remove unnecessary whitespace from the question
    question = question.strip()

    # Validate the question
    if not question:
        raise ValueError("The question cannot be empty.")

    # Validate the number of results
    if top_k <= 0:
        raise ValueError("top_k must be greater than zero.")
        # Convert the question into an embedding
    question_embedding = generate_embedding(question)
        # Check the number of stored chunks
    total_chunks = research_collection.count()

    # Return an empty list if no chunks are stored
    if total_chunks == 0:
        return []

    # Avoid requesting more results than are available
    results_to_retrieve = min(top_k, total_chunks)
        # Search ChromaDB for the most relevant chunks
    search_results = research_collection.query(
        query_embeddings=[question_embedding],
        n_results=results_to_retrieve,
        include=["documents", "metadatas", "distances"]
    )
        # Extract results for the submitted question
    retrieved_chunks = []

    # Get the results returned by ChromaDB
    chunk_ids = search_results["ids"][0]
    documents = search_results["documents"][0]
    metadatas = search_results["metadatas"][0]
    distances = search_results["distances"][0]

    # Combine each retrieved chunk with its metadata
    for chunk_id, document, metadata, distance in zip(
        chunk_ids, documents, metadatas, distances
    ):
        retrieved_chunks.append({
            "chunk_id": chunk_id,
            "text": document,
            "document_id": metadata["document_id"],
            "filename": metadata["filename"],
            "page_number": metadata["page_number"],
            "distance": distance
        })
            # Return the retrieved chunks
    return retrieved_chunks