import type { DocumentResponse } from '../types'

interface DocumentCardProps {
  doc: DocumentResponse
}

export function DocumentCard({ doc }: DocumentCardProps): JSX.Element {
  return (
    <div className="border border-gray-200 rounded-lg p-6 space-y-3 bg-gray-50">
      <div className="flex items-center justify-between">
        <span className="font-semibold text-gray-900 text-lg">{doc.filename}</span>
        <span className="text-xs bg-gray-200 text-gray-700 px-2 py-1 rounded">{doc.document_type}</span>
      </div>
      <div className="grid grid-cols-2 gap-2 text-sm text-gray-600">
        <span>Pages: <strong className="text-gray-900">{doc.page_count}</strong></span>
        <span>Confidence: <strong className="text-gray-900">{(doc.classification_confidence * 100).toFixed(1)}%</strong></span>
        <span>Embedding: <strong className="text-gray-900">{doc.embedding_stored ? 'stored' : 'not stored'}</strong></span>
        <span className="truncate" title={doc.document_id}>ID: <strong className="text-gray-900 text-xs">{doc.document_id}</strong></span>
      </div>
      <div>
        <p className="text-xs font-medium text-gray-500 mb-1 uppercase tracking-wide">Extracted fields</p>
        <pre className="text-xs bg-white border border-gray-200 rounded p-3 overflow-auto max-h-64 text-gray-800">
          {JSON.stringify(doc.fields, null, 2)}
        </pre>
      </div>
    </div>
  )
}
