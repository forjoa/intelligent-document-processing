import { useRef, useState } from 'react'
import { uploadDocument } from '../api'
import type { DocumentResponse } from '../types'
import { DocumentCard } from './DocumentCard'
import { Spinner } from './Spinner'

export function UploadView(): JSX.Element {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<DocumentResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [dragging, setDragging] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  function reset(): void {
    setResult(null)
    setError(null)
  }

  async function process(file: File): Promise<void> {
    if (file.type !== 'application/pdf') {
      setError('Only PDF files are accepted.')
      return
    }
    reset()
    setLoading(true)
    try {
      const doc = await uploadDocument(file)
      setResult(doc)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed.')
    } finally {
      setLoading(false)
    }
  }

  function onDrop(e: React.DragEvent<HTMLDivElement>): void {
    e.preventDefault()
    setDragging(false)
    const file = e.dataTransfer.files[0]
    if (file) void process(file)
  }

  function onFileChange(e: React.ChangeEvent<HTMLInputElement>): void {
    const file = e.target.files?.[0]
    if (file) void process(file)
  }

  return (
    <div className="space-y-6">
      <div
        className={`border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-colors ${
          dragging ? 'border-gray-700 bg-gray-100' : 'border-gray-300 hover:border-gray-500'
        }`}
        onDragOver={(e) => { e.preventDefault(); setDragging(true) }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
        onClick={() => inputRef.current?.click()}
      >
        <input ref={inputRef} type="file" accept=".pdf,application/pdf" className="hidden" onChange={onFileChange} />
        <p className="text-gray-500 text-sm">Drag & drop a PDF here, or click to browse</p>
      </div>

      {loading && (
        <div className="flex items-center gap-3 text-gray-600 text-sm">
          <Spinner />
          <span>Processing document…</span>
        </div>
      )}

      {error && (
        <p className="text-sm text-gray-900 bg-gray-100 border border-gray-300 rounded px-4 py-3">{error}</p>
      )}

      {result && <DocumentCard doc={result} />}
    </div>
  )
}
