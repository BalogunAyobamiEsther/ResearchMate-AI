import pytest

from backend.app.services.chunker import chunk_text


def test_chunk_text():
    """Test that text is divided into overlapping chunks."""

    pages = [
        {
            "page_number": 1,
            "text": "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        }
    ]

    chunks = chunk_text(
        pages,
        chunk_size=10,
        chunk_overlap=3
    )

    assert len(chunks) == 4
    assert chunks[0]["text"] == "ABCDEFGHIJ"
    assert chunks[1]["text"] == "HIJKLMNOPQ"
    assert chunks[2]["text"] == "OPQRSTUVWX"
    assert chunks[3]["text"] == "VWXYZ"


def test_chunk_page_number_is_preserved():
    """Test that each chunk retains its original page number."""

    pages = [
        {
            "page_number": 3,
            "text": "This is a sample research document."
        }
    ]

    chunks = chunk_text(pages, chunk_size=15, chunk_overlap=5)

    assert all(chunk["page_number"] == 3 for chunk in chunks)


def test_chunk_ids_are_unique():
    """Test that every generated chunk has a unique ID."""

    pages = [
        {
            "page_number": 1,
            "text": "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        }
    ]

    chunks = chunk_text(pages, chunk_size=10, chunk_overlap=3)

    chunk_ids = [chunk["chunk_id"] for chunk in chunks]

    assert len(chunk_ids) == len(set(chunk_ids))


def test_zero_chunk_size():
    """Test that zero chunk size is rejected."""

    pages = [{"page_number": 1, "text": "Sample text"}]

    with pytest.raises(ValueError, match="Chunk size must be greater than zero"):
        chunk_text(pages, chunk_size=0, chunk_overlap=0)


def test_negative_chunk_size():
    """Test that negative chunk size is rejected."""

    pages = [{"page_number": 1, "text": "Sample text"}]

    with pytest.raises(ValueError, match="Chunk size must be greater than zero"):
        chunk_text(pages, chunk_size=-5, chunk_overlap=0)


def test_negative_overlap():
    """Test that negative overlap is rejected."""

    pages = [{"page_number": 1, "text": "Sample text"}]

    with pytest.raises(ValueError, match="Chunk overlap cannot be negative"):
        chunk_text(pages, chunk_size=10, chunk_overlap=-1)


def test_overlap_equal_to_chunk_size():
    """Test that overlap equal to chunk size is rejected."""

    pages = [{"page_number": 1, "text": "Sample text"}]

    with pytest.raises(ValueError, match="Chunk overlap must be smaller than chunk size"):
        chunk_text(pages, chunk_size=10, chunk_overlap=10)