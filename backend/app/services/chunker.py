from uuid import uuid4


def chunk_text(
    pages: list[dict],
    chunk_size: int = 800,
    chunk_overlap: int = 150
) -> list[dict]:
    """
    Divide extracted PDF text into smaller overlapping chunks.

    Args:
        pages: List of dictionaries containing page numbers and text.
        chunk_size: Maximum number of characters per chunk.
        chunk_overlap: Number of characters shared between chunks.

    Returns:
        A list of dictionaries containing chunk IDs, page numbers,
        and chunk text.
    """

    # Validate chunk size
    if chunk_size <= 0:
        raise ValueError("Chunk size must be greater than zero.")

    # Validate chunk overlap
    if chunk_overlap < 0:
        raise ValueError("Chunk overlap cannot be negative.")

    if chunk_overlap >= chunk_size:
        raise ValueError("Chunk overlap must be smaller than chunk size.")

    chunks = []

    # Calculate how far to move before creating the next chunk
    step_size = chunk_size - chunk_overlap

    # Process each page independently
    for page in pages:

        text = page["text"].strip()
        page_number = page["page_number"]

        # Skip empty pages
        if not text:
            continue

        # Divide the page into overlapping chunks
        for start in range(0, len(text), step_size):

            end = start + chunk_size

            chunk = text[start:end].strip()

            # Store only non-empty chunks
            if chunk:
                chunks.append({
                    "chunk_id": str(uuid4()),
                    "page_number": page_number,
                    "text": chunk
                })

            # Stop when the end of the page is reached
            if end >= len(text):
                break

    return chunks