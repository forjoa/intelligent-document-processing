export interface DocumentResponse {
  document_id: string
  filename: string
  page_count: number
  document_type: string
  classification_confidence: number
  fields: Record<string, unknown>
  embedding_stored: boolean
}

export interface SearchResult {
  document_id: string
  filename: string
  document_type: string
  similarity: number
  fields: Record<string, unknown>
}

export interface SearchResponse {
  query: string
  top_n: number
  results: SearchResult[]
}

export interface DocumentListItem {
  document_id: string
  filename: string
  document_type: string
  created_at: string
  fields: Record<string, unknown>
}

export interface DocumentListResponse {
  documents: DocumentListItem[]
  total: number
}

export type Tab = 'upload' | 'search'
