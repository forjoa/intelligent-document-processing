import type { SearchResult } from '../types'

interface SearchResultCardProps {
  result: SearchResult
}

export function SearchResultCard({ result }: SearchResultCardProps): JSX.Element {
  return (
    <div className="border border-gray-200 rounded-lg p-5 space-y-3 bg-gray-50">
      <div className="flex items-center justify-between">
        <span className="font-medium text-gray-900">{result.filename}</span>
        <div className="flex gap-2 items-center">
          <span className="text-xs bg-gray-200 text-gray-700 px-2 py-1 rounded">{result.document_type}</span>
          <span className="text-xs font-mono text-gray-500">{(result.similarity * 100).toFixed(1)}% match</span>
        </div>
      </div>
      <pre className="text-xs bg-white border border-gray-200 rounded p-3 overflow-auto max-h-48 text-gray-800">
        {JSON.stringify(result.fields, null, 2)}
      </pre>
    </div>
  )
}
