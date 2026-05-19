from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api import documents, health
from app.core.database import init_db
from app.core.dependencies import load_embedder, load_nlp, load_paddle_ocr
from app.core.exceptions import (
    DatabaseError,
    DocumentProcessingError,
    EmbeddingError,
    ExtractionError,
    FileTooLarge,
    NonPDFFile,
    OCRFailure,
    TooManyPages,
)

_EXCEPTION_STATUS: dict[type[DocumentProcessingError], int] = {
    FileTooLarge: 413,
    NonPDFFile: 415,
    TooManyPages: 422,
    OCRFailure: 422,
    ExtractionError: 422,
    EmbeddingError: 500,
    DatabaseError: 500,
}

_EXCEPTION_CODE: dict[type[DocumentProcessingError], str] = {
    FileTooLarge: "FILE_TOO_LARGE",
    NonPDFFile: "NON_PDF_FILE",
    TooManyPages: "TOO_MANY_PAGES",
    OCRFailure: "OCR_FAILURE",
    ExtractionError: "EXTRACTION_ERROR",
    EmbeddingError: "EMBEDDING_ERROR",
    DatabaseError: "DATABASE_ERROR",
}


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    load_paddle_ocr()
    load_nlp()
    load_embedder()
    await init_db()
    yield


app = FastAPI(title="Intelligent Document Processing", lifespan=lifespan)


def _make_error_handler(exc_class: type[DocumentProcessingError]):
    async def handler(request: Request, exc: DocumentProcessingError) -> JSONResponse:
        return JSONResponse(
            status_code=_EXCEPTION_STATUS[exc_class],
            content={"error": str(exc), "code": _EXCEPTION_CODE[exc_class]},
        )
    return handler


for _exc_class in _EXCEPTION_STATUS:
    app.add_exception_handler(_exc_class, _make_error_handler(_exc_class))

app.include_router(health.router)
app.include_router(documents.router)
