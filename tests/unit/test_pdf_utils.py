import os
os.environ.setdefault("DATABASE_URL", "postgresql://test")

import io
import struct
import pytest
import fitz

from app.utils.pdf import validate_pdf, pdf_to_images
from app.core.exceptions import NonPDFFile, FileTooLarge


def _make_minimal_pdf() -> bytes:
    """Create a valid single-page PDF in memory using pymupdf."""
    doc = fitz.open()
    doc.new_page(width=100, height=100)
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


def test_validate_pdf_non_pdf_bytes_raises() -> None:
    with pytest.raises(NonPDFFile):
        validate_pdf(b"this is not a pdf", "test.txt")


def test_validate_pdf_jpeg_header_raises() -> None:
    with pytest.raises(NonPDFFile):
        validate_pdf(b"\xff\xd8\xff\xe0fake jpeg data", "image.jpg")


def test_validate_pdf_too_large_raises() -> None:
    # Build bytes > 20 MB that start with %PDF so it passes magic check
    large = b"%PDF" + b"\x00" * (21 * 1024 * 1024)
    with pytest.raises(FileTooLarge):
        validate_pdf(large, "big.pdf")


def test_validate_pdf_valid_passes() -> None:
    pdf_bytes = _make_minimal_pdf()
    # Should not raise
    validate_pdf(pdf_bytes, "valid.pdf")


def test_pdf_to_images_single_page_returns_one_item() -> None:
    pdf_bytes = _make_minimal_pdf()
    images = pdf_to_images(pdf_bytes)
    assert len(images) == 1


def test_pdf_to_images_returns_png_bytes() -> None:
    pdf_bytes = _make_minimal_pdf()
    images = pdf_to_images(pdf_bytes)
    # PNG magic bytes
    assert images[0][:8] == b"\x89PNG\r\n\x1a\n"


def test_pdf_to_images_multipage() -> None:
    doc = fitz.open()
    for _ in range(3):
        doc.new_page(width=100, height=100)
    buf = io.BytesIO()
    doc.save(buf)
    images = pdf_to_images(buf.getvalue())
    assert len(images) == 3
