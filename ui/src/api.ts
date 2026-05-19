import type { DocumentListResponse, DocumentResponse, SearchResponse } from './types'

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let message = res.statusText
    try {
      const body = (await res.json()) as { error?: string }
      if (body.error) message = body.error
    } catch {
      // ignore parse failure
    }
    throw new Error(message)
  }
  return res.json() as Promise<T>
}

export async function uploadDocument(file: File): Promise<DocumentResponse> {
  const form = new FormData()
  form.append('file', file)
  const res = await fetch('/documents/upload', { method: 'POST', body: form })
  return handleResponse<DocumentResponse>(res)
}

export async function listDocuments(): Promise<DocumentListResponse> {
  const res = await fetch('/documents')
  return handleResponse<DocumentListResponse>(res)
}

export async function searchDocuments(query: string, topN: number): Promise<SearchResponse> {
  const params = new URLSearchParams({ query, top_n: String(topN) })
  const res = await fetch(`/documents/search?${params.toString()}`)
  return handleResponse<SearchResponse>(res)
}
