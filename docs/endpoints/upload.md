# POST /documents/upload

Accepts a PDF file, runs the full processing pipeline (OCR → classify → extract → embed), persists the result, and returns structured JSON.

---

## Request

**Method:** `POST`  
**Path:** `/documents/upload`  
**Content-Type:** `multipart/form-data`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | file | yes | PDF binary |

**Constraints**
- File must be a valid PDF (`application/pdf`)
- Maximum size: 20 MB
- Maximum pages: 50

---

## curl Example

```bash
curl -X POST http://localhost:8000/documents/upload \
  -F "file=@invoice.pdf"
```

---

## Success Response — 200

```json
{
  "document_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "filename": "invoice.pdf",
  "page_count": 2,
  "document_type": "invoice",
  "classification_confidence": 0.82,
  "fields": {
    "company": "Acme Corp",
    "date": "May 1, 2026",
    "total": "1,250.00",
    "currency": "USD",
    "invoice_number": "INV-20260501"
  },
  "embedding_stored": true
}
```

`fields` content varies by `document_type`. See the [field taxonomy](../../SPEC.md#per-class-extracted-fields) for per-class shapes. For `document_type: "unknown"`, `fields` is `{}`.

---

## Error Responses

All error bodies follow the shape: `{ "error": "string", "code": "string" }`

### 413 — File Too Large

```json
{
  "error": "File exceeds the 20 MB limit",
  "code": "FILE_TOO_LARGE"
}
```

### 415 — Unsupported Media Type

```json
{
  "error": "Only PDF files are accepted",
  "code": "NON_PDF_FILE"
}
```

### 422 — Unprocessable

Returned for page count violations, OCR failure, or extraction errors.

```json
{
  "error": "PDF exceeds the 50-page limit",
  "code": "TOO_MANY_PAGES"
}
```

```json
{
  "error": "OCR produced no usable text",
  "code": "OCR_FAILURE"
}
```

```json
{
  "error": "spaCy pipeline failed: ...",
  "code": "EXTRACTION_ERROR"
}
```
