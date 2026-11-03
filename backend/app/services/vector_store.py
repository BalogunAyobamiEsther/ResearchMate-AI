import chromadb

from backend.app.core.config import settings


# Create a persistent ChromaDB client
chroma_client = chromadb.PersistentClient(
    path=settings.CHROMA_DB_PATH
)


# Create or retrieve the ResearchMate collection
research_collection = chroma_client.get_or_create_collection(
    name="research_documents",
    metadata={
        "description": "ResearchMate AI document embeddings",
        "hnsw:space": "cosine"
    }
)


def add_chunks_to_collection(
    chunks: list[dict],
    embeddings: list[list[float]],
    document_id: str,
    filename: str
) -> None:
    """
    Store document chunks, embeddings, and metadata in ChromaDB.

    Args:
        chunks: List of text chunks with IDs and page numbers.
        embeddings: Numerical embeddings corresponding to each chunk.
        document_id: Unique identifier for the uploaded document.
        filename: Original PDF filename.
    """

    # Check that every chunk has a corresponding embedding
    if len(chunks) != len(embeddings):
        raise ValueError(
            "The number of chunks must match the number of embeddings."
        )

    # Prepare the metadata for each chunk
    metadatas = [
        {
            "document_id": document_id,
            "filename": filename,
            "page_number": chunk["page_number"]
        }
        for chunk in chunks
    ]

    # Store the chunks in ChromaDB
    research_collection.add(
        ids=[chunk["chunk_id"] for chunk in chunks],
        embeddings=embeddings,
        documents=[chunk["text"] for chunk in chunks],
        metadatas=metadatas
    )


def get_all_documents() -> list[dict]:
    """
    Retrieve all unique documents stored in ChromaDB.

    Returns:
        A list containing document information and chunk counts.
    """

    # Retrieve metadata for all stored chunks
    results = research_collection.get(
        include=["metadatas"]
    )

    documents = {}

    # Group chunks by their document ID
    for metadata in results["metadatas"]:

        document_id = metadata["document_id"]

        if document_id not in documents:
            documents[document_id] = {
                "document_id": document_id,
                "filename": metadata["filename"],
                "total_chunks": 0
            }

        # Count chunks belonging to this document
        documents[document_id]["total_chunks"] += 1

    return list(documents.values())


def delete_document(document_id: str) -> bool:
    """
    Delete a document and all its chunks from ChromaDB.

    Args:
        document_id: Unique ID of the document to delete.

    Returns:
        True if the document was found and deleted.
        False if the document does not exist.
    """

    # Check whether the document exists
    results = research_collection.get(
        where={"document_id": document_id},
        include=["metadatas"]
    )

    # Return False if no chunks belong to this document
    if not results["ids"]:
        return False

    # Delete all chunks belonging to this document
    research_collection.delete(
        where={"document_id": document_id}
    )

    return True


def get_document_details(document_id: str) -> dict | None:
    """
    Retrieve details about a specific document.

    Args:
        document_id: Unique ID of the document.

    Returns:
        Document information or None if the document doesn't exist.
    """

    # Retrieve all chunks belonging to the document
    results = research_collection.get(
        where={"document_id": document_id},
        include=["metadatas"]
    )

    # Check whether the document exists
    if not results["ids"]:
        return None

    # Extract the document metadata
    metadatas = results["metadatas"]

    # Count the unique pages represented in the document
    total_pages = len({
        metadata["page_number"]
        for metadata in metadatas
    })

    return {
        "document_id": document_id,
        "filename": metadatas[0]["filename"],
        "total_chunks": len(results["ids"]),
        "total_pages": total_pages
    }