import pymupdf
from pathlib import Path


def extract_text_from_pdf(pdf_path: str) -> list[dict]:
    """
    Extract text from a PDF while preserving original page numbers.

    Args:
        pdf_path: Path to the PDF document.

    Returns:
        A list of dictionaries containing page numbers and extracted text.

    Raises:
        FileNotFoundError: If the PDF does not exist.
        ValueError: If the file is invalid, unsupported, encrypted,
                    empty, or contains no extractable text.
    """

    pdf_file = Path(pdf_path)

    # Check whether the PDF exists
    if not pdf_file.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    # Check the file extension
    if pdf_file.suffix.lower() != ".pdf":
        raise ValueError("Only PDF files are supported.")

    try:
        # Open the PDF document
        with pymupdf.open(pdf_file) as document:

            # Check whether the PDF is password-protected
            if document.needs_pass:
                raise ValueError("Password-protected PDFs are not supported.")

            # Check whether the PDF contains pages
            if document.page_count == 0:
                raise ValueError("The PDF document is empty.")

            extracted_pages = []

            # Process each page
            for page_number, page in enumerate(document, start=1):

                # Extract text from the current page
                text = page.get_text("text").strip()

                # Store non-empty pages
                if text:
                    extracted_pages.append({
                        "page_number": page_number,
                        "text": text
                    })

            # Check whether any text was extracted
            if not extracted_pages:
                raise ValueError(
                    "No extractable text found. "
                    "The PDF may contain scanned images instead of text."
                )

            return extracted_pages

    except pymupdf.FileDataError as error:
        raise ValueError(
            "The uploaded file is not a valid or readable PDF."
        ) from error