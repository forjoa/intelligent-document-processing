import { describe, it, expect, vi, beforeEach } from 'vitest'
import { uploadDocument, searchDocuments } from '../api'
import type { DocumentResponse, SearchResponse } from '../types'

const mockDocumentResponse: DocumentResponse = {
  document_id: 'doc-123',
  filename: 'invoice.pdf',
  page_count: 2,
  document_type: 'invoice',
  classification_confidence: 0.95,
  fields: { total: 129.99 },
  embedding_stored: true,
}

const mockSearchResponse: SearchResponse = {
  query: 'invoice',
  top_n: 5,
  results: [
    {
      document_id: 'doc-123',
      filename: 'invoice.pdf',
      document_type: 'invoice',
      similarity: 0.87,
      fields: { total: 129.99 },
    },
  ],
}

beforeEach(() => {
  vi.restoreAllMocks()
})

describe('uploadDocument', () => {
  it('sends POST to /documents/upload with FormData and returns DocumentResponse', async () => {
    const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify(mockDocumentResponse), { status: 200 }),
    )

    const file = new File(['%PDF-1.4'], 'invoice.pdf', { type: 'application/pdf' })
    const result = await uploadDocument(file)

    expect(fetchSpy).toHaveBeenCalledOnce()
    const [url, init] = fetchSpy.mock.calls[0] as [string, RequestInit]
    expect(url).toBe('/documents/upload')
    expect(init.method).toBe('POST')
    expect(init.body).toBeInstanceOf(FormData)
    expect(result).toEqual(mockDocumentResponse)
  })

  it('throws with error message from response body on non-2xx', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify({ error: 'File too large' }), { status: 413 }),
    )

    const file = new File(['%PDF-1.4'], 'big.pdf', { type: 'application/pdf' })
    await expect(uploadDocument(file)).rejects.toThrow('File too large')
  })

  it('throws with statusText when error body has no error field', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify({}), { status: 500, statusText: 'Internal Server Error' }),
    )

    const file = new File(['%PDF-1.4'], 'invoice.pdf', { type: 'application/pdf' })
    await expect(uploadDocument(file)).rejects.toThrow('Internal Server Error')
  })

  it('throws with statusText when response body is not JSON', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response('not json', { status: 503, statusText: 'Service Unavailable' }),
    )

    const file = new File(['%PDF-1.4'], 'invoice.pdf', { type: 'application/pdf' })
    await expect(uploadDocument(file)).rejects.toThrow('Service Unavailable')
  })
})

describe('searchDocuments', () => {
  it('sends GET to /documents/search with query and top_n params and returns SearchResponse', async () => {
    const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify(mockSearchResponse), { status: 200 }),
    )

    const result = await searchDocuments('invoice', 5)

    expect(fetchSpy).toHaveBeenCalledOnce()
    const [url] = fetchSpy.mock.calls[0] as [string]
    expect(url).toBe('/documents/search?query=invoice&top_n=5')
    expect(result).toEqual(mockSearchResponse)
  })

  it('throws with error message from response body on non-2xx', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify({ error: 'Query too short' }), { status: 400 }),
    )

    await expect(searchDocuments('a', 5)).rejects.toThrow('Query too short')
  })

  it('throws with statusText on non-2xx without JSON error body', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response('not json', { status: 502, statusText: 'Bad Gateway' }),
    )

    await expect(searchDocuments('invoice', 5)).rejects.toThrow('Bad Gateway')
  })
})
