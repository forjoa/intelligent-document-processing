import asyncio
import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.database import AsyncSessionLocal
from app.core.exceptions import DatabaseError
from app.models.db import Document
from app.models.schemas import DocumentResponse
from app.services.classifier import classify
from app.services.embedder import embed
from app.services.extractor import extract_fields
from app.services.ocr import run_ocr
from app.utils.pdf import pdf_to_images, validate_pdf


async def process_document(
    file_bytes: bytes,
    filename: str,
    session: AsyncSession,
    paddle_ocr: Any,
    nlp: Any,
    embedder: Any,
    settings: Settings,
) -> DocumentResponse:
    validate_pdf(file_bytes, filename)
    images = pdf_to_images(file_bytes)

    loop = asyncio.get_running_loop()

    # Run heavy CPU-bound work before acquiring any DB connection.
    ocr_result = await loop.run_in_executor(
        None,
        lambda: run_ocr(images, paddle_ocr, settings.OCR_CONFIDENCE_THRESHOLD),
    )

    classification = classify(ocr_result.text, settings.CLASSIFICATION_MIN_CONFIDENCE)
    fields = extract_fields(ocr_result.text, classification.document_type, nlp)

    vector = await loop.run_in_executor(
        None,
        lambda: embed(ocr_result.text, embedder),
    )

    doc = Document(
        id=uuid.uuid4(),
        filename=filename,
        page_count=len(images),
        document_type=classification.document_type,
        classification_confidence=classification.confidence,
        extracted_fields=fields,
        raw_text=ocr_result.text,
        embedding=vector,
    )

    # Open a fresh session for the insert so we never use a stale connection.
    try:
        async with AsyncSessionLocal() as fresh_session:
            fresh_session.add(doc)
            await fresh_session.commit()
            await fresh_session.refresh(doc)
    except Exception as exc:
        raise DatabaseError(f"Failed to persist document: {exc}") from exc

    return DocumentResponse(
        document_id=doc.id,
        filename=doc.filename,
        page_count=doc.page_count,
        document_type=doc.document_type,
        classification_confidence=doc.classification_confidence,
        fields=doc.extracted_fields,
        embedding_stored=doc.embedding is not None,
    )
