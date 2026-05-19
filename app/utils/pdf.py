import io

import fitz  # pymupdf

from app.core.config import settings
from app.core.exceptions import FileTooLarge, NonPDFFile, TooManyPages

_PDF_MAGIC = b"%PDF"


def validate_pdf(file_bytes: bytes, filename: str) -> None:
    if not file_bytes.startswith(_PDF_MAGIC):
        raise NonPDFFile(f"{filename!r} is not a PDF file")
    size_mb = len(file_bytes) / (1024 * 1024)
    if size_mb > settings.MAX_FILE_SIZE_MB:
        raise FileTooLarge(
            f"{filename!r} is {size_mb:.1f} MB; limit is {settings.MAX_FILE_SIZE_MB} MB"
        )


def pdf_to_images(file_bytes: bytes) -> list[bytes]:
    doc = fitz.open(stream=io.BytesIO(file_bytes), filetype="pdf")
    if doc.page_count > settings.MAX_PAGES:
        raise TooManyPages(
            f"Document has {doc.page_count} pages; limit is {settings.MAX_PAGES}"
        )
    images: list[bytes] = []
    for page in doc:
        pix = page.get_pixmap(dpi=150)
        images.append(pix.tobytes("png"))
    return images
