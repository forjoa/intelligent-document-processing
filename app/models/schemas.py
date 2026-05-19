from typing import Any
from uuid import UUID

from pydantic import BaseModel


class DocumentResponse(BaseModel):
    document_id: UUID
    filename: str
    page_count: int
    document_type: str
    classification_confidence: float
    fields: dict[str, Any]
    embedding_stored: bool


class SearchResult(BaseModel):
    document_id: UUID
    filename: str
    document_type: str
    similarity: float
    fields: dict[str, Any]


class SearchResponse(BaseModel):
    query: str
    top_n: int
    results: list[SearchResult]


class DocumentListItem(BaseModel):
    document_id: UUID
    filename: str
    document_type: str
    created_at: str
    fields: dict[str, Any]


class DocumentListResponse(BaseModel):
    documents: list[DocumentListItem]
    total: int


class HealthResponse(BaseModel):
    status: str
    detail: str | None = None


class ErrorResponse(BaseModel):
    error: str
    code: str
