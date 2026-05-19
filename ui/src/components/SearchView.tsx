import { useEffect, useState } from 'react'
import { listDocuments, searchDocuments } from '../api'
import type { DocumentListItem, SearchResult } from '../types'
import { SearchResultCard } from './SearchResultCard'
import { Spinner } from './Spinner'

const TOP_N = 5

export function SearchView(): JSX.Element {
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState<SearchResult[]>([])
  const [error, setError] = useState<string | null>(null)
  const [searched, setSearched] = useState(false)
  const [documents, setDocuments] = useState<DocumentListItem[]>([])
  const [docsLoading, setDocsLoading] = useState(true)
  const [docsError, setDocsError] = useState<string | null>(null)

  useEffect(() => {
    listDocuments()
      .then((res) => setDocuments(res.documents))
      .catch((err) => setDocsError(err instanceof Error ? err.message : 'Failed to load documents.'))
      .finally(() => setDocsLoading(false))
  }, [])

  async function onSearch(): Promise<void> {
    const q = query.trim()
    if (!q) {
      setError('Enter a search query.')
      return
    }
    setError(null)
    setLoading(true)
    setSearched(false)
    try {
      const res = await searchDocuments(q, TOP_N)
      setResults(res.results)
      setSearched(true)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed.')
    } finally {
      setLoading(false)
    }
  }

  function onKeyDown(e: React.KeyboardEvent<HTMLInputElement>): void {
    if (e.key === 'Enter') void onSearch()
  }

  return (
    <div className="space-y-6">
      <div className="flex gap-3">
        <input
          type="text"
          className="flex-1 border border-gray-300 rounded px-4 py-2 text-sm focus:outline-none focus:border-gray-700"
          placeholder="Search documents…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={onKeyDown}
        />
        <button
          className="px-5 py-2 bg-gray-900 text-white text-sm rounded hover:bg-gray-700 transition-colors disabled:opacity-50"
          onClick={() => void onSearch()}
          disabled={loading}
        >
          Search
        </button>
      </div>

      {loading && (
        <div className="flex items-center gap-3 text-gray-600 text-sm">
          <Spinner />
          <span>Searching…</span>
        </div>
      )}

      {error && (
        <p className="text-sm text-gray-900 bg-gray-100 border border-gray-300 rounded px-4 py-3">{error}</p>
      )}

      {searched && results.length === 0 && (
        <p className="text-sm text-gray-500">No results found.</p>
      )}

      {searched && results.length > 0 && (
        <div className="space-y-4">
          {results.map((r) => (
            <SearchResultCard key={r.document_id} result={r} />
          ))}
        </div>
      )}

      {!searched && (
        <div>
          <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-3">Scanned documents</p>
          {docsLoading && (
            <div className="flex items-center gap-3 text-gray-600 text-sm">
              <Spinner />
              <span>Loading…</span>
            </div>
          )}
          {docsError && (
            <p className="text-sm text-gray-900 bg-gray-100 border border-gray-300 rounded px-4 py-3">{docsError}</p>
          )}
          {!docsLoading && !docsError && documents.length === 0 && (
            <p className="text-sm text-gray-500">No documents scanned yet.</p>
          )}
          {!docsLoading && documents.length > 0 && (
            <ul className="space-y-2">
              {documents.map((doc) => (
                <li key={doc.document_id} className="flex items-center justify-between border border-gray-200 rounded px-4 py-3 text-sm">
                  <span className="font-medium text-gray-800 truncate">{doc.filename}</span>
                  <span className="ml-4 shrink-0 text-xs text-gray-500 bg-gray-100 rounded px-2 py-0.5">{doc.document_type}</span>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  )
}
