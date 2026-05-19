# Intelligent Document Processing — Specification

## System Overview

An HTTP API that accepts PDF documents, runs OCR, classifies the document type, extracts structured fields per class, stores a semantic embedding, and persists all results to PostgreSQL. Supports semantic search over ingested documents via pgvector cosine similarity.

---

## Endpoints

### POST /documents/upload
Accepts a PDF file, processes it through the full pipeline, and returns structured output.

### GET /documents/search
Accepts a natural-language query, embeds it, and returns the top-N most semantically similar documents.

### GET /health
Returns database reachability status.

---

## Request / Response Shapes

### POST /documents/upload

**Request**
- Content-Type: `multipart/form-data`
- Field: `file` — PDF binary

**Constraints**
- Max file size: 20 MB (`MAX_FILE_SIZE_MB`)
- Max pages: 50 (`MAX_PAGES`)
- Accepted MIME: `application/pdf` only

**Response 200**
```json
{
  "document_id": "uuid",
  "filename": "string",
  "page_count": "integer",
  "document_type": "string",
  "classification_confidence": "float",
  "fields": "object",
  "embedding_stored": "boolean"
}
```

**Error Responses**

| HTTP | code | condition |
|------|------|-----------|
| 413 | `FILE_TOO_LARGE` | file exceeds 20 MB |
| 415 | `NON_PDF_FILE` | file is not a PDF |
| 422 | `TOO_MANY_PAGES` | PDF exceeds 50 pages |
| 422 | `OCR_FAILURE` | OCR produced no usable text |
| 422 | `EXTRACTION_ERROR` | spaCy pipeline failed |
| 500 | `EMBEDDING_ERROR` | embedding model failed |
| 500 | `DATABASE_ERROR` | persistence failed |

Error body: `{ "error": "string", "code": "string" }`

---

### GET /documents/search

**Query Parameters**

| Name | Type | Required | Default | Constraints |
|------|------|----------|---------|-------------|
| `query` | string | yes | — | min length 1 |
| `top_n` | integer | no | 5 | 1 – 20 |

**Response 200**
```json
{
  "query": "string",
  "top_n": "integer",
  "results": [
    {
      "document_id": "uuid",
      "filename": "string",
      "document_type": "string",
      "similarity": "float",
      "fields": "object"
    }
  ]
}
```

**Error Responses**

| HTTP | condition |
|------|-----------|
| 422 | `query` missing or empty; `top_n` out of range |

---

### GET /health

**Response 200 — healthy**
```json
{ "status": "ok" }
```

**Response 503 — degraded** (returned with HTTP 200 per current implementation, status field signals degradation)
```json
{ "status": "degraded", "detail": "database unreachable" }
```

---

## Document Type Taxonomy

| Type | Description |
|------|-------------|
| `invoice` | Billing documents, receipts with amount due |
| `ticket` | Event tickets, boarding passes, transit tickets |
| `contract` | Legal agreements, NDAs, service contracts |
| `cv` | Resumes and curriculum vitae |
| `unknown` | Classifier confidence below threshold (0.4) or no signal |

Classification uses keyword scoring. Confidence = winner score / total score across all classes. Falls back to `unknown` when confidence < `CLASSIFICATION_MIN_CONFIDENCE` (0.4).

---

## Per-Class Extracted Fields

### invoice
| Field | Source |
|-------|--------|
| `company` | spaCy `ORG` entity |
| `date` | spaCy `DATE` entity |
| `total` | regex on "total / amount due / balance due" |
| `currency` | regex (USD, EUR, GBP, CAD, AUD, $, €, £) |
| `invoice_number` | regex on "invoice #/No./:" |

### ticket
| Field | Source |
|-------|--------|
| `event_or_route` | spaCy `EVENT`, `FAC`, `LOC`, or `ORG` entity |
| `date` | spaCy `DATE` entity |
| `seat_or_section` | regex on "seat / row / section" |
| `price` | regex on currency-prefixed number |

### contract
| Field | Source |
|-------|--------|
| `parties` | spaCy `ORG` and `PERSON` entities (deduplicated) |
| `effective_date` | spaCy `DATE` entity |
| `governing_law` | regex on "governing law" clause |

### cv
| Field | Source |
|-------|--------|
| `name` | spaCy `PERSON` entity |
| `email` | regex |
| `phone` | regex |
| `skills` | regex block under "Skills:" heading |
| `experience` | regex blocks matching title / org / period pattern |

For `unknown` documents, `fields` is `{}`.

---

## Database Schema

Table: `documents`

| Column | Type | Notes |
|--------|------|-------|
| `id` | UUID (PK) | auto-generated |
| `filename` | VARCHAR | original filename |
| `page_count` | INTEGER | |
| `document_type` | VARCHAR | one of the five types |
| `classification_confidence` | FLOAT | |
| `extracted_fields` | JSONB | per-class fields dict |
| `raw_text` | TEXT | full OCR output |
| `embedding` | vector(384) | pgvector; nullable |
| `created_at` | TIMESTAMPTZ | server default `now()` |

Embedding model: `all-MiniLM-L6-v2` (384 dimensions). IVFFlat index with 100 lists.

---

## Error Response Format

All application errors return:
```json
{
  "error": "human-readable message",
  "code": "SCREAMING_SNAKE_CASE_CODE"
}
```

FastAPI validation errors (422) from query parameter constraints use the default FastAPI error shape.

---

## Runtime Constraints

| Setting | Value |
|---------|-------|
| Max file size | 20 MB |
| Max pages | 50 |
| OCR confidence threshold | 0.8 |
| Classification min confidence | 0.4 |
| Embedding model | all-MiniLM-L6-v2 |
| IVFFlat lists | 100 |
| Default search top_n | 5 |
| OCR primary | PaddleOCR |
| OCR fallback | Tesseract |
