from fastapi import APIRouter, Depends, Query, UploadFile
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.dependencies import get_embedder, get_nlp, get_paddle_ocr, get_session
from app.models.schemas import DocumentListItem, DocumentListResponse, DocumentResponse, SearchResponse, SearchResult
from app.services.embedder import embed
from app.services.pipeline import process_document

router = APIRouter()


@router.get("/documents", response_model=DocumentListResponse)
async def list_documents(
    session: AsyncSession = Depends(get_session),
) -> DocumentListResponse:
    stmt = text(
        "SELECT id, filename, document_type, created_at, extracted_fields FROM documents ORDER BY created_at DESC"
    )
    result = await session.execute(stmt)
    rows = result.fetchall()
    items = [
        DocumentListItem(
            document_id=row.id,
            filename=row.filename,
            document_type=row.document_type,
            created_at=row.created_at.isoformat(),
            fields=row.extracted_fields,
        )
        for row in rows
    ]
    return DocumentListResponse(documents=items, total=len(items))


@router.post("/documents/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile,
    session: AsyncSession = Depends(get_session),
) -> DocumentResponse:
    file_bytes = await file.read()
    return await process_document(
        file_bytes=file_bytes,
        filename=file.filename or "unknown.pdf",
        session=session,
        paddle_ocr=get_paddle_ocr(),
        nlp=get_nlp(),
        embedder=get_embedder(),
        settings=settings,
    )


@router.get("/documents/search", response_model=SearchResponse)
async def search_documents(
    query: str = Query(..., min_length=1),
    top_n: int = Query(default=5, ge=1, le=20),
    session: AsyncSession = Depends(get_session),
) -> SearchResponse:
    embedder = get_embedder()
    query_vector = embed(query, embedder)
    vector_literal = f"[{','.join(str(v) for v in query_vector)}]"

    stmt = text(
        """
        SELECT
            id,
            filename,
            document_type,
            extracted_fields,
            1 - (embedding <=> CAST(:vector AS vector)) AS similarity
        FROM documents
        WHERE embedding IS NOT NULL
        ORDER BY embedding <=> CAST(:vector AS vector)
        LIMIT :top_n
        """
    )
    result = await session.execute(stmt, {"vector": vector_literal, "top_n": top_n})
    rows = result.fetchall()

    results = [
        SearchResult(
            document_id=row.id,
            filename=row.filename,
            document_type=row.document_type,
            similarity=float(row.similarity),
            fields=row.extracted_fields,
        )
        for row in rows
    ]

    return SearchResponse(query=query, top_n=top_n, results=results)
