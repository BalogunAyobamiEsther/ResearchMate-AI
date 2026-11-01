import pytest

from backend.app.services.prompt_builder import build_rag_prompt


# Sample research passages for testing
sample_chunks = [
    {
        "chunk_id": "chunk-001",
        "document_id": "doc-001",
        "filename": "biology_research.pdf",
        "page_number": 2,
        "text": "The study adopted a descriptive survey research design."
    },
    {
        "chunk_id": "chunk-002",
        "document_id": "doc-001",
        "filename": "biology_research.pdf",
        "page_number": 4,
        "text": "Data were collected using structured questionnaires."
    }
]


def test_build_rag_prompt():
    """Test successful construction of a RAG prompt."""

    result = build_rag_prompt(
        question="What research methodology was used?",
        retrieved_chunks=sample_chunks
    )

    assert "prompt" in result
    assert "sources" in result

    assert "What research methodology was used?" in result["prompt"]

    assert "[SOURCE S1]" in result["prompt"]
    assert "[SOURCE S2]" in result["prompt"]

    assert len(result["sources"]) == 2


def test_source_metadata_is_preserved():
    """Test that source identifiers retain their original metadata."""

    result = build_rag_prompt(
        question="How was data collected?",
        retrieved_chunks=sample_chunks
    )

    first_source = result["sources"][0]

    assert first_source["source_id"] == "S1"
    assert first_source["chunk_id"] == "chunk-001"
    assert first_source["document_id"] == "doc-001"
    assert first_source["filename"] == "biology_research.pdf"
    assert first_source["page_number"] == 2


def test_empty_question():
    """Test that an empty question is rejected."""

    with pytest.raises(ValueError):
        build_rag_prompt(
            question="",
            retrieved_chunks=sample_chunks
        )


def test_whitespace_question():
    """Test that a whitespace-only question is rejected."""

    with pytest.raises(ValueError):
        build_rag_prompt(
            question="   ",
            retrieved_chunks=sample_chunks
        )


def test_empty_retrieved_chunks():
    """Test that an empty retrieval result is rejected."""

    with pytest.raises(ValueError):
        build_rag_prompt(
            question="What methodology was used?",
            retrieved_chunks=[]
        )