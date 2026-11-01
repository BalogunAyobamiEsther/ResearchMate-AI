from pathlib import Path
from uuid import uuid4

from backend.app.core.config import settings
from backend.app.services.pdf_processor import extract_text_from_pdf
from backend.app.services.chunker import chunk_text
from backend.app.services.embedding_service import generate_embeddings
from backend.app.services.vector_store import add_chunks_to_collection

def ingest_document(pdf_path: str) -> dict:
    """
    Process a PDF document and store its embeddings in ChromaDB.

    Args:
        pdf_path: Path to the PDF document.

    Returns:
        A dictionary containing document information and ingestion statistics.
    """

    # Convert the supplied path into a Path object
    pdf_file = Path(pdf_path)

    # Check whether the PDF exists
    if not pdf_file.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    # Generate a unique ID for this document
    document_id = str(uuid4())

    # Get the original PDF filename
    filename = pdf_file.name
    
    # Step 1: Extract text from the PDF
    pages = extract_text_from_pdf(str(pdf_file))

    # Step 2: Divide the extracted text into chunks
    chunks = chunk_text(
        pages=pages,
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP
    )
    
    # Step 3: Generate embeddings for all chunks
    texts = [chunk["text"] for chunk in chunks]

    embeddings = generate_embeddings(texts)
    # Step 4: Store chunks and embeddings in ChromaDB
    add_chunks_to_collection(
        chunks=chunks,
        embeddings=embeddings,
        document_id=document_id,
        filename=filename
    )
    # Step 5: Return ingestion information
    return {
        "document_id": document_id,
        "filename": filename,
        "total_pages": len(pages),
        "total_chunks": len(chunks),
        "total_embeddings": len(embeddings),
        "status": "success"
    }