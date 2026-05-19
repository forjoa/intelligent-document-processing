# Changelog

## [Unreleased]

### Added
- Invoice extraction now returns `line_items` inside `fields` — each item has `description`, `quantity`, `unit_price`, and `amount` (`str | null`); extraction is language- and format-agnostic, using numeric token detection and region anchoring

## [0.2.0] - 2026-05-20

### Added
- React + Vite + TypeScript + TailwindCSS web UI under `ui/`
- TypeScript interfaces for API response shapes: `DocumentResponse`, `SearchResult`, `SearchResponse`, `Tab`
- Typed fetch wrappers `uploadDocument()` and `searchDocuments()` in `ui/src/api.ts`
- UI components: `TabNav`, `UploadView`, `SearchView`, `DocumentCard`, `SearchResultCard`, `Spinner`
- Two-tab app (`Upload` / `Search`) in `ui/src/App.tsx`
- Vite dev proxy: `/documents/*` → `http://localhost:8000` (no CORS config needed)
- `run.sh` now starts the UI dev server in background (step 7) and kills it on EXIT
- `npm run start` launches the dev server at `http://localhost:5173`

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
