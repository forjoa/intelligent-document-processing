# GET /documents/search

Embeds the query string and returns the top-N documents ranked by cosine similarity against stored embeddings. Only documents with a stored embedding are considered.

---

## Request

**Method:** `GET`  
**Path:** `/documents/search`

| Parameter | Type | Required | Default | Constraints |
|-----------|------|----------|---------|-------------|
| `query` | string | yes | — | min length 1 |
| `top_n` | integer | no | 5 | 1 – 20 |

---

## curl Example

```bash
curl "http://localhost:8000/documents/search?query=software+engineer+Python&top_n=3"
```

---

## Success Response — 200

```json
{
  "query": "software engineer Python",
  "top_n": 3,
  "results": [
    {
      "document_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "filename": "john_doe_cv.pdf",
      "document_type": "cv",
      "similarity": 0.91,
      "fields": {
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "+1 555 123 4567",
        "skills": ["Python", "FastAPI", "PostgreSQL"],
        "experience": [
          {
            "title": "Senior Software Engineer",
            "organization": "Acme Corp",
            "period": "2021 – present"
          }
        ]
      }
    }
  ]
}
```

`similarity` is in [0, 1] (cosine similarity via pgvector `<=>` operator; 1 = identical). Results are ordered descending by similarity.

---

## Error Responses

### 422 — Validation Error

Returned by FastAPI when `query` is missing or empty, or `top_n` is outside [1, 20].

```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["query", "query"],
      "msg": "Field required"
    }
  ]
}
```
