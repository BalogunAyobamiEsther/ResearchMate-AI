import pytest

from unittest.mock import patch

from backend.app.schemas.chat import LLMResponse
from backend.app.services.rag_service import answer_research_question


# Valid test session ID.
SESSION_ID = "a" * 43


# Sample retrieved research passages.
sample_chunks = [
    {
        "chunk_id": "chunk-001",
        "document_id": "doc-001",
        "filename": "biology_research.pdf",
        "page_number": 2,
        "text": "The study adopted a descriptive survey research design.",
    },
    {
        "chunk_id": "chunk-002",
        "document_id": "doc-001",
        "filename": "biology_research.pdf",
        "page_number": 4,
        "text": "Data were collected using structured questionnaires.",
    },
]


def test_missing_session_id():
    """Test that a missing session ID is rejected."""

    with pytest.raises(ValueError):
        answer_research_question(
            question="What research methodology was used?",
            owner_session_id="",
        )


def test_empty_question():
    """Test that an empty research question is rejected."""

    with pytest.raises(ValueError):
        answer_research_question(
            question="",
            owner_session_id=SESSION_ID,
        )


def test_no_retrieved_chunks():
    """Test behaviour when no research passages are found."""

    with patch(
        "backend.app.services.rag_service.retrieve_relevant_chunks",
        return_value=[],
    ) as mock_retrieval:

        result = answer_research_question(
            question="What research methodology was used?",
            owner_session_id=SESSION_ID,
        )

    mock_retrieval.assert_called_once_with(
        question="What research methodology was used?",
        owner_session_id=SESSION_ID,
        top_k=5,
    )

    assert result["insufficient_evidence"] is True
    assert result["citations"] == []
    assert result["evidence"] == []


def test_successful_rag_generation():
    """Test successful answer generation with valid citations."""

    generated_answer = (
        "The study adopted a descriptive survey design [S1]. "
        "Data were collected using questionnaires [S2]."
    )

    with patch(
        "backend.app.services.rag_service.retrieve_relevant_chunks",
        return_value=sample_chunks,
    ) as mock_retrieval:

        with patch(
            "backend.app.services.rag_service.generate_response",
            return_value=LLMResponse(
                answer=generated_answer,
                insufficient_evidence=False,
            ),
        ):

            result = answer_research_question(
                question="What research methodology was used?",
                owner_session_id=SESSION_ID,
            )

    mock_retrieval.assert_called_once_with(
        question="What research methodology was used?",
        owner_session_id=SESSION_ID,
        top_k=5,
    )

    assert result["answer"] == generated_answer
    assert result["insufficient_evidence"] is False

    assert len(result["citations"]) == 2

    assert result["citations"][0]["source_id"] == "S1"
    assert result["citations"][0]["page_number"] == 2

    assert result["citations"][1]["source_id"] == "S2"
    assert result["citations"][1]["page_number"] == 4


def test_invalid_citations_are_rejected():
    """Test that references not supplied to Gemini are rejected."""

    generated_answer = (
        "The study used an experimental design [S9]."
    )

    with patch(
        "backend.app.services.rag_service.retrieve_relevant_chunks",
        return_value=sample_chunks,
    ):

        with patch(
            "backend.app.services.rag_service.generate_response",
            return_value=LLMResponse(
                answer=generated_answer,
                insufficient_evidence=False,
            ),
        ):

            result = answer_research_question(
                question="What research methodology was used?",
                owner_session_id=SESSION_ID,
            )

    assert result["citations"] == []
    assert result["insufficient_evidence"] is True


def test_duplicate_citations_are_removed():
    """Test that repeated source references are not duplicated."""

    generated_answer = (
        "The study used a survey design [S1]. "
        "The methodology is confirmed in [S1]."
    )

    with patch(
        "backend.app.services.rag_service.retrieve_relevant_chunks",
        return_value=sample_chunks,
    ):

        with patch(
            "backend.app.services.rag_service.generate_response",
            return_value=LLMResponse(
                answer=generated_answer,
                insufficient_evidence=False,
            ),
        ):

            result = answer_research_question(
                question="What research methodology was used?",
                owner_session_id=SESSION_ID,
            )

    assert len(result["citations"]) == 1
    assert result["citations"][0]["source_id"] == "S1"