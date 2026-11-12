
from pathlib import Path
from uuid import uuid4
import shutil

from backend.app.core.config import settings
from backend.app.services.pdf_processor import extract_text_from_pdf
from backend.app.services.chunker import chunk_text
from backend.app.services.embedding_service import generate_embeddings
from backend.app.services.vector_store import add_chunks_to_collection


def ingest_document(
    pdf_path: str,
    owner_session_id: str,
    original_filename: str | None = None,
) -> dict:
    """
    Process a PDF document, save the original PDF permanently,
    and store its embeddings with browser session ownership.
    """

    if not owner_session_id:
        raise ValueError("A valid owner session ID is required.")

    pdf_file = Path(pdf_path)

    if not pdf_file.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    # Generate a unique ID for this document.
    document_id = str(uuid4())

    # Get the original PDF filename.
    filename = original_filename or pdf_file.name

    # Create the permanent document storage directory.
    storage_directory = Path(settings.DOCUMENT_STORAGE_PATH)
    storage_directory.mkdir(parents=True, exist_ok=True)

    # Save the original PDF using its unique document ID.
    permanent_pdf_path = storage_directory / f"{document_id}.pdf"

    try:
        shutil.copy2(pdf_file, permanent_pdf_path)

        # Step 1: Extract text from the PDF.
        pages = extract_text_from_pdf(str(pdf_file))

        # Step 2: Divide extracted text into chunks.
        chunks = chunk_text(
            pages=pages,
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
        )

        # Step 3: Generate embeddings.
        texts = [chunk["text"] for chunk in chunks]
        embeddings = generate_embeddings(texts)

        # Step 4: Store chunks, embeddings, and ownership metadata.
        add_chunks_to_collection(
            chunks=chunks,
            embeddings=embeddings,
            document_id=document_id,
            filename=filename,
            owner_session_id=owner_session_id,
        )

        # Step 5: Return ingestion information.
        return {
            "document_id": document_id,
            "filename": filename,
            "total_pages": len(pages),
            "total_chunks": len(chunks),
            "total_embeddings": len(embeddings),
            "status": "success",
        }

    except Exception:
        # Remove the saved PDF if ingestion fails.
        if permanent_pdf_path.exists():
            permanent_pdf_path.unlink()

        raise
