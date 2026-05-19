# GET /health

Returns the operational status of the API. Performs a live database probe (`SELECT 1`) on every call.

---

## Request

**Method:** `GET`  
**Path:** `/health`

No parameters, no request body.

---

## curl Example

```bash
curl http://localhost:8000/health
```

---

## Success Response — 200 (healthy)

```json
{
  "status": "ok"
}
```

---

## Degraded Response — 200 (database unreachable)

The HTTP status is still `200`. Callers must inspect the `status` field to detect degradation.

```json
{
  "status": "degraded",
  "detail": "database unreachable"
}
```

`detail` is only present when `status` is `"degraded"`.
