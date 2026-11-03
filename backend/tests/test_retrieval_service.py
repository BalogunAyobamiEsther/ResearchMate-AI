
import pytest

from unittest.mock import patch

from backend.app.services.retrieval_service import retrieve_relevant_chunks


def test_empty_question():
    """Test that an empty question raises a ValueError."""

    with pytest.raises(
        ValueError,
        match="The question cannot be empty."
    ):
        retrieve_relevant_chunks("")


def test_question_containing_only_whitespace():
    """Test that a whitespace-only question is rejected."""

    with pytest.raises(
        ValueError,
        match="The question cannot be empty."
    ):
        retrieve_relevant_chunks("     ")


@pytest.mark.parametrize("top_k", [0, -1])
def test_invalid_top_k(top_k):
    """Test that zero and negative top_k values are rejected."""

    with pytest.raises(
        ValueError,
        match="top_k must be greater than zero."
    ):
        retrieve_relevant_chunks(
            question="What is the research methodology?",
            top_k=top_k
        )


def test_retrieve_relevant_chunks():
    """Test successful retrieval of relevant document chunks."""

    question = "What is the research methodology?"

    mock_results = {
        "ids": [["chunk-1"]],
        "documents": [
            ["The study adopted a descriptive survey design."]
        ],
        "metadatas": [[
            {
                "document_id": "doc-1",
                "filename": "research.pdf",
                "page_number": 2
            }
        ]],
        "distances": [[0.12]]
    }

    with patch(
        "backend.app.services.retrieval_service.generate_embedding",
        return_value=[0.1, 0.2]
    ) as mock_embedding:

        with patch(
            "backend.app.services.retrieval_service.research_collection"
        ) as mock_collection:

            mock_collection.count.return_value = 10
            mock_collection.query.return_value = mock_results

            results = retrieve_relevant_chunks(question)

    assert len(results) == 1
    assert results[0]["chunk_id"] == "chunk-1"
    assert results[0]["text"] == (
        "The study adopted a descriptive survey design."
    )
    assert results[0]["document_id"] == "doc-1"
    assert results[0]["filename"] == "research.pdf"
    assert results[0]["page_number"] == 2
    assert results[0]["distance"] == 0.12

    mock_embedding.assert_called_once_with(question)

    mock_collection.query.assert_called_once_with(
        query_embeddings=[[0.1, 0.2]],
        n_results=10,
        include=["documents", "metadatas", "distances"]
    )


def test_retrieve_from_empty_collection():
    """Test retrieval when the vector database contains no chunks."""

    with patch(
        "backend.app.services.retrieval_service.generate_embedding",
        return_value=[0.1, 0.2]
    ):

        with patch(
            "backend.app.services.retrieval_service.research_collection"
        ) as mock_collection:

            mock_collection.count.return_value = 0

            results = retrieve_relevant_chunks(
                "What is the research methodology?"
            )

    assert results == []

    mock_collection.query.assert_not_called()


def test_top_k_does_not_exceed_available_chunks():
    """Test that retrieval is limited to available chunks."""

    mock_results = {
        "ids": [["chunk-1", "chunk-2"]],
        "documents": [[
            "The study used a survey design.",
            "Data were collected using questionnaires."
        ]],
        "metadatas": [[
            {
                "document_id": "doc-1",
                "filename": "research.pdf",
                "page_number": 2
            },
            {
                "document_id": "doc-1",
                "filename": "research.pdf",
                "page_number": 3
            }
        ]],
        "distances": [[0.12, 0.18]]
    }

    with patch(
        "backend.app.services.retrieval_service.generate_embedding",
        return_value=[0.1, 0.2]
    ):

        with patch(
            "backend.app.services.retrieval_service.research_collection"
        ) as mock_collection:

            mock_collection.count.return_value = 2
            mock_collection.query.return_value = mock_results

            results = retrieve_relevant_chunks(
                question="How was the study conducted?",
                top_k=5
            )

    assert len(results) == 2

    mock_collection.query.assert_called_once_with(
        query_embeddings=[[0.1, 0.2]],
        n_results=2,
        include=["documents", "metadatas", "distances"]
    )


def test_duplicate_chunks_are_removed():
    """Test that identical passages from different documents are removed."""

    mock_results = {
        "ids": [
            ["chunk-1", "chunk-2", "chunk-3", "chunk-4"]
        ],
        "documents": [[
            "The study adopted a descriptive survey design.",
            "The study adopted a descriptive survey design.",
            "Data were collected using questionnaires.",
            "The study adopted a descriptive survey design."
        ]],
        "metadatas": [[
            {
                "document_id": "doc-1",
                "filename": "research1.pdf",
                "page_number": 2
            },
            {
                "document_id": "doc-2",
                "filename": "research2.pdf",
                "page_number": 2
            },
            {
                "document_id": "doc-1",
                "filename": "research1.pdf",
                "page_number": 3
            },
            {
                "document_id": "doc-3",
                "filename": "research3.pdf",
                "page_number": 2
            }
        ]],
        "distances": [[0.10, 0.11, 0.15, 0.17]]
    }

    with patch(
        "backend.app.services.retrieval_service.generate_embedding",
        return_value=[0.1, 0.2]
    ):

        with patch(
            "backend.app.services.retrieval_service.research_collection"
        ) as mock_collection:

            mock_collection.count.return_value = 9
            mock_collection.query.return_value = mock_results

            results = retrieve_relevant_chunks(
                question="What research design was adopted?",
                top_k=3
            )

    assert len(results) == 2

    assert results[0]["chunk_id"] == "chunk-1"
    assert results[0]["document_id"] == "doc-1"

    assert results[1]["chunk_id"] == "chunk-3"
    assert results[1]["text"] == (
        "Data were collected using questionnaires."
    )

    mock_collection.query.assert_called_once_with(
        query_embeddings=[[0.1, 0.2]],
        n_results=9,
        include=["documents", "metadatas", "distances"]
    )


def test_duplicate_chunks_with_different_whitespace_are_removed():
    """Test that whitespace differences do not prevent deduplication."""

    mock_results = {
        "ids": [["chunk-1", "chunk-2"]],
        "documents": [[
            "The study adopted a descriptive survey design.",
            "  The study adopted a descriptive\nsurvey design.  "
        ]],
        "metadatas": [[
            {
                "document_id": "doc-1",
                "filename": "research1.pdf",
                "page_number": 2
            },
            {
                "document_id": "doc-2",
                "filename": "research2.pdf",
                "page_number": 2
            }
        ]],
        "distances": [[0.10, 0.12]]
    }

    with patch(
        "backend.app.services.retrieval_service.generate_embedding",
        return_value=[0.1, 0.2]
    ):

        with patch(
            "backend.app.services.retrieval_service.research_collection"
        ) as mock_collection:

            mock_collection.count.return_value = 2
            mock_collection.query.return_value = mock_results

            results = retrieve_relevant_chunks(
                "What research design was adopted?",
                top_k=2
            )

    assert len(results) == 1
    assert results[0]["chunk_id"] == "chunk-1"
