from fastapi import APIRouter, UploadFile, File, HTTPException, status

from pathlib import Path
import tempfile

from backend.app.core.config import settings
from backend.app.services.ingestion_service import ingest_document
from backend.app.services.vector_store import (
    get_all_documents,
    delete_document,
    get_document_details
)


# Create the documents API router
router = APIRouter()

# Retrieve all uploaded research documents
@router.get(
    "/documents",
    status_code=status.HTTP_200_OK,
    tags=["Documents"]
)
def list_documents():
    """
    Retrieve all documents stored in ResearchMate AI.
    """

    documents = get_all_documents()

    return {
        "total_documents": len(documents),
        "documents": documents
    }
    
# Retrieve details of a specific research document
@router.get(
    "/documents/{document_id}",
    status_code=status.HTTP_200_OK,
    tags=["Documents"]
)
def retrieve_document(document_id: str):
    """
    Retrieve details of a specific uploaded document.
    """

    document = get_document_details(document_id)

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found."
        )

    return document

# PDF document upload endpoint
@router.post(
    "/documents/upload",
    status_code=status.HTTP_201_CREATED,
    tags=["Documents"]
)
def upload_document(file: UploadFile = File(...)):
    """
    Upload and process an academic research PDF.
    """

    # Check the uploaded file extension
    if Path(file.filename or "").suffix.lower() != ".pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported."
        )

    # Read the uploaded file, allowing one extra byte
    # to detect files that exceed the configured limit
    file_content = file.file.read(
        settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024 + 1
    )

    # Check the uploaded file size
    if len(file_content) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="The uploaded file exceeds the maximum allowed size."
        )

    # Reject empty files
    if not file_content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file is empty."
        )

    # Create a temporary PDF file
    temporary_path = None

    try:
        with tempfile.NamedTemporaryFile(
            suffix=".pdf",
            delete=False
        ) as temporary_file:

            temporary_file.write(file_content)
            temporary_path = temporary_file.name

        # Process the uploaded PDF
        result = ingest_document(
    pdf_path=temporary_path,
    original_filename=file.filename
)

        return {
            "message": "Document uploaded and processed successfully.",
            "document": result
        }

    except (ValueError, FileNotFoundError) as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        ) from error

    finally:
        # Remove the temporary PDF after processing
        if temporary_path and Path(temporary_path).exists():
            Path(temporary_path).unlink()

        file.file.close()
        
# Delete an uploaded research document
@router.delete(
    "/documents/{document_id}",
    status_code=status.HTTP_200_OK,
    tags=["Documents"]
)
def remove_document(document_id: str):
    """
    Delete a document and all its chunks from ChromaDB.
    """

    deleted = delete_document(document_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found."
        )

    return {
        "message": "Document deleted successfully.",
        "document_id": document_id
    }