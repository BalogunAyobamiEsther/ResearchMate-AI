
import chromadb

from backend.app.core.config import settings


# Create a persistent ChromaDB client.
chroma_client = chromadb.PersistentClient(
    path=settings.CHROMA_DB_PATH
)


# Create or retrieve the existing ResearchMate collection.
research_collection = chroma_client.get_or_create_collection(
    name=settings.CHROMA_COLLECTION_NAME,
    metadata={
        "description": "ResearchMate AI document embeddings",
        "hnsw:space": "cosine",
    },
)


def add_chunks_to_collection(
    chunks: list[dict],
    embeddings: list[list[float]],
    document_id: str,
    filename: str,
    owner_session_id: str,
) -> None:
    """
    Store document chunks, embeddings, and ownership metadata in ChromaDB.
    """

    if len(chunks) != len(embeddings):
        raise ValueError(
            "The number of chunks must match the number of embeddings."
        )

    if not owner_session_id:
        raise ValueError("A valid owner session ID is required.")

    metadatas = [
        {
            "document_id": document_id,
            "filename": filename,
            "page_number": chunk["page_number"],
            "owner_session_id": owner_session_id,
        }
        for chunk in chunks
    ]

    research_collection.add(
        ids=[chunk["chunk_id"] for chunk in chunks],
        embeddings=embeddings,
        documents=[chunk["text"] for chunk in chunks],
        metadatas=metadatas,
    )


def get_all_documents(owner_session_id: str) -> list[dict]:
    """
    Retrieve only documents belonging to a specific browser session.
    """

    if not owner_session_id:
        return []

    results = research_collection.get(
        where={"owner_session_id": owner_session_id},
        include=["metadatas"],
    )

    documents = {}

    for metadata in results["metadatas"] or []:
        document_id = metadata["document_id"]

        if document_id not in documents:
            documents[document_id] = {
                "document_id": document_id,
                "filename": metadata["filename"],
                "total_chunks": 0,
            }

        documents[document_id]["total_chunks"] += 1

    return list(documents.values())


def delete_document(
    document_id: str,
    owner_session_id: str,
) -> bool:
    """
    Delete a document only if it belongs to the given browser session.
    """

    if not owner_session_id:
        return False

    ownership_filter = {
        "$and": [
            {"document_id": document_id},
            {"owner_session_id": owner_session_id},
        ]
    }

    results = research_collection.get(
        where=ownership_filter,
        include=["metadatas"],
    )

    if not results["ids"]:
        return False

    research_collection.delete(
        where=ownership_filter,
    )

    return True


def get_document_details(
    document_id: str,
    owner_session_id: str,
) -> dict | None:
    """
    Retrieve document details only if it belongs to the given session.
    """

    if not owner_session_id:
        return None

    ownership_filter = {
        "$and": [
            {"document_id": document_id},
            {"owner_session_id": owner_session_id},
        ]
    }

    results = research_collection.get(
        where=ownership_filter,
        include=["metadatas"],
    )

    if not results["ids"]:
        return None

    metadatas = results["metadatas"] or []

    total_pages = len({
        metadata["page_number"]
        for metadata in metadatas
    })

    return {
        "document_id": document_id,
        "filename": metadatas[0]["filename"],
        "total_chunks": len(results["ids"]),
        "total_pages": total_pages,
    }
