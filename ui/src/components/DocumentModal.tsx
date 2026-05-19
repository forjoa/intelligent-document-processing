import { useEffect } from 'react'
import type { DocumentListItem } from '../types'

interface DocumentModalProps {
  doc: DocumentListItem
  onClose: () => void
}

export function DocumentModal({ doc, onClose }: DocumentModalProps): JSX.Element {
  useEffect(() => {
    function onKey(e: KeyboardEvent): void {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [onClose])

  const fields = Object.entries(doc.fields)
  const date = new Date(doc.created_at).toLocaleString()

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-2xl shadow-2xl w-full max-w-lg max-h-[80vh] flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-start justify-between px-6 pt-6 pb-4 border-b border-gray-100">
          <div className="space-y-1 min-w-0 pr-4">
            <p className="font-semibold text-gray-900 truncate">{doc.filename}</p>
            <div className="flex items-center gap-2">
              <span className="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full">{doc.document_type}</span>
              <span className="text-xs text-gray-400">{date}</span>
            </div>
          </div>
          <button
            onClick={onClose}
            className="shrink-0 text-gray-400 hover:text-gray-700 transition-colors text-xl leading-none"
            aria-label="Close"
          >
            ×
          </button>
        </div>

        <div className="px-6 py-5 overflow-y-auto">
          {fields.length === 0 ? (
            <p className="text-sm text-gray-400">No extracted fields.</p>
          ) : (
            <dl className="space-y-3">
              {fields.map(([key, value]) => (
                <div key={key} className="flex flex-col gap-0.5">
                  <dt className="text-xs font-medium text-gray-400 uppercase tracking-wide">{key.replace(/_/g, ' ')}</dt>
                  <dd className="text-sm text-gray-800 bg-gray-50 rounded-lg px-3 py-2 break-words">
                    {typeof value === 'object' ? JSON.stringify(value, null, 2) : String(value ?? '—')}
                  </dd>
                </div>
              ))}
            </dl>
          )}
        </div>
      </div>
    </div>
  )
}
