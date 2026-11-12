
from pathlib import Path

import chromadb
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.core.config import settings
from backend.app.services import vector_store


SESSION_ONE = "a" * 43
SESSION_TWO = "b" * 43

DOCUMENT_ONE = "private-document-one"
DOCUMENT_TWO = "private-document-two"


@pytest.fixture
def isolated_document_environment(tmp_path, monkeypatch):
    """
    Provide an isolated ChromaDB collection and temporary PDF storage.
    Never access the persistent ResearchMate collection.
    """

    client = chromadb.EphemeralClient()

    collection = client.create_collection(
        name="researchmate_isolation_test",
        metadata={"hnsw:space": "cosine"},
    )

    monkeypatch.setattr(
        vector_store,
        "research_collection",
        collection,
    )

    document_directory = tmp_path / "documents"
    document_directory.mkdir()

    monkeypatch.setattr(
        settings,
        "DOCUMENT_STORAGE_PATH",
        str(document_directory),
    )

    # Add a document belonging to browser one.
    collection.add(
        ids=["chunk-one"],
        embeddings=[[0.1, 0.2, 0.3]],
        documents=["Private research belonging to browser one."],
        metadatas=[
            {
                "document_id": DOCUMENT_ONE,
                "filename": "private-one.pdf",
                "page_number": 1,
                "owner_session_id": SESSION_ONE,
            }
        ],
    )

    # Add a document belonging to browser two.
    collection.add(
        ids=["chunk-two"],
        embeddings=[[0.4, 0.5, 0.6]],
        documents=["Private research belonging to browser two."],
        metadatas=[
            {
                "document_id": DOCUMENT_TWO,
                "filename": "private-two.pdf",
                "page_number": 1,
                "owner_session_id": SESSION_TWO,
            }
        ],
    )

    # Create a temporary PDF placeholder for browser one's document.
    pdf_path = document_directory / f"{DOCUMENT_ONE}.pdf"
    pdf_path.write_bytes(b"%PDF-1.4\nTest PDF content")

    return collection, document_directory


def test_documents_are_isolated_between_browser_sessions(
    isolated_document_environment,
):
    collection, document_directory = isolated_document_environment

    browser_one = TestClient(app)
    browser_two = TestClient(app)

    browser_one.cookies.set(
        settings.SESSION_COOKIE_NAME,
        SESSION_ONE,
    )

    browser_two.cookies.set(
        settings.SESSION_COOKIE_NAME,
        SESSION_TWO,
    )

    origin = {"Origin": "http://localhost:5173"}

    # Browser one should see only its own document.
    own_documents = browser_one.get("/api/v1/documents")

    assert own_documents.status_code == 200
    assert own_documents.json()["total_documents"] == 1
    assert (
        own_documents.json()["documents"][0]["document_id"]
        == DOCUMENT_ONE
    )

    # Browser two should see only its own document.
    other_documents = browser_two.get("/api/v1/documents")

    assert other_documents.status_code == 200
    assert other_documents.json()["total_documents"] == 1
    assert (
        other_documents.json()["documents"][0]["document_id"]
        == DOCUMENT_TWO
    )

    # Browser two cannot access browser one's document details.
    other_details = browser_two.get(
        f"/api/v1/documents/{DOCUMENT_ONE}"
    )

    assert other_details.status_code == 404

    # Browser two cannot download browser one's PDF.
    other_file = browser_two.get(
        f"/api/v1/documents/{DOCUMENT_ONE}/file"
    )

    assert other_file.status_code == 404

    # Browser two cannot delete browser one's document.
    other_delete = browser_two.delete(
        f"/api/v1/documents/{DOCUMENT_ONE}",
        headers=origin,
    )

    assert other_delete.status_code == 404

    # Browser one's document must remain accessible.
    own_details = browser_one.get(
        f"/api/v1/documents/{DOCUMENT_ONE}"
    )

    assert own_details.status_code == 200
    assert own_details.json()["filename"] == "private-one.pdf"

    # Browser one can still download its original PDF.
    own_file = browser_one.get(
        f"/api/v1/documents/{DOCUMENT_ONE}/file"
    )

    assert own_file.status_code == 200
    assert own_file.headers["content-type"] == "application/pdf"

    # Browser one can delete its own document.
    own_delete = browser_one.delete(
        f"/api/v1/documents/{DOCUMENT_ONE}",
        headers=origin,
    )

    assert own_delete.status_code == 200

    # Its ChromaDB chunks should now be deleted.
    remaining = collection.get(
        where={
            "owner_session_id": SESSION_ONE,
        },
        include=["metadatas"],
    )

    assert DOCUMENT_ONE not in [
        metadata["document_id"]
        for metadata in remaining["metadatas"]
    ]

    # Browser two's document must remain untouched.
    other_document_after_deletion = browser_two.get(
        f"/api/v1/documents/{DOCUMENT_TWO}"
    )

    assert other_document_after_deletion.status_code == 200

    # The original PDF belonging to browser one should be removed.
    assert not (
        document_directory / f"{DOCUMENT_ONE}.pdf"
    ).exists()
