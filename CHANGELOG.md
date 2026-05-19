# Changelog

## [0.1.0] - 2026-05-19

### Added
- Initial project scaffold
- OCR pipeline: PaddleOCR primary, Tesseract fallback
- Document classification (invoice, ticket, contract, cv) using keyword scoring
- Per-class field extraction using spaCy NER and regex
- Semantic embedding storage via pgvector (all-MiniLM-L6-v2, 384 dimensions)
- POST /documents/upload endpoint — accepts PDF, returns structured JSON
- GET /documents/search endpoint — semantic similarity search over ingested documents
- GET /health endpoint — returns database reachability status
- 36 unit tests (100% pass rate)
