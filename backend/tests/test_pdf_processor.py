import pymupdf
import pytest

from backend.app.services.pdf_processor import extract_text_from_pdf


def create_test_pdf(pdf_path):
    """Create a small PDF for testing."""

    document = pymupdf.open()

    page = document.new_page()
    page.insert_text((72, 72), "ResearchMate AI testing document.")

    document.save(pdf_path)
    document.close()


def test_extract_text_from_pdf(tmp_path):
    """Test that text is successfully extracted from a PDF."""

    # Arrange: Create a temporary PDF
    pdf_path = tmp_path / "sample.pdf"
    create_test_pdf(pdf_path)

    # Act: Extract text from the PDF
    pages = extract_text_from_pdf(str(pdf_path))

    # Assert: Verify the extracted result
    assert len(pages) == 1
    assert pages[0]["page_number"] == 1
    assert "ResearchMate AI testing document." in pages[0]["text"]
    
def test_missing_pdf_file():
    """Test that a missing PDF raises FileNotFoundError."""

    with pytest.raises(FileNotFoundError):
        extract_text_from_pdf("nonexistent.pdf")
        
def test_unsupported_file_extension(tmp_path):
    """Test that non-PDF files are rejected."""

    # Arrange: Create a text file
    text_file = tmp_path / "sample.txt"
    text_file.write_text("This is not a PDF.")

    # Act and Assert
    with pytest.raises(ValueError, match="Only PDF files are supported"):
        extract_text_from_pdf(str(text_file))
        
def test_corrupted_pdf_file(tmp_path):
    """Test that corrupted PDFs raise a clear ValueError."""

    # Arrange: Create a fake PDF
    corrupted_pdf = tmp_path / "corrupted.pdf"
    corrupted_pdf.write_text("This is not a valid PDF document.")

    # Act and Assert
    with pytest.raises(ValueError, match="not a valid or readable PDF"):
        extract_text_from_pdf(str(corrupted_pdf))
        
def test_pdf_without_extractable_text(tmp_path):
    """Test that PDFs without extractable text raise ValueError."""

    # Arrange: Create a blank PDF page
    pdf_path = tmp_path / "blank.pdf"

    document = pymupdf.open()
    document.new_page()
    document.save(pdf_path)
    document.close()

    # Act and Assert
    with pytest.raises(ValueError, match="No extractable text found"):
        extract_text_from_pdf(str(pdf_path))