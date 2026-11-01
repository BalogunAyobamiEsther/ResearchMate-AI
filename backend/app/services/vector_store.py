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