import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { SearchView } from '../components/SearchView'
import * as api from '../api'
import type { SearchResponse } from '../types'

const mockSearchResponse: SearchResponse = {
  query: 'invoice',
  top_n: 5,
  results: [
    {
      document_id: 'doc-1',
      filename: 'invoice.pdf',
      document_type: 'invoice',
      similarity: 0.9,
      fields: {},
    },
  ],
}

beforeEach(() => {
  vi.restoreAllMocks()
})

describe('SearchView', () => {
  it('shows inline error and does not call fetch when query is empty', async () => {
    const searchSpy = vi.spyOn(api, 'searchDocuments')
    render(<SearchView />)

    await userEvent.click(screen.getByRole('button', { name: /search/i }))

    expect(screen.getByText('Enter a search query.')).toBeInTheDocument()
    expect(searchSpy).not.toHaveBeenCalled()
  })

  it('shows spinner while search is in progress', async () => {
    let resolveSearch!: (value: SearchResponse) => void
    vi.spyOn(api, 'searchDocuments').mockReturnValue(
      new Promise<SearchResponse>((res) => { resolveSearch = res }),
    )

    render(<SearchView />)

    await userEvent.type(screen.getByPlaceholderText('Search documents…'), 'invoice')
    await userEvent.click(screen.getByRole('button', { name: /search/i }))

    expect(screen.getByText('Searching…')).toBeInTheDocument()

    resolveSearch(mockSearchResponse)
    await waitFor(() => expect(screen.queryByText('Searching…')).not.toBeInTheDocument())
  })

  it('triggers search on Enter key press', async () => {
    const searchSpy = vi.spyOn(api, 'searchDocuments').mockResolvedValue(mockSearchResponse)
    render(<SearchView />)

    await userEvent.type(screen.getByPlaceholderText('Search documents…'), 'invoice{Enter}')

    await waitFor(() => expect(searchSpy).toHaveBeenCalledWith('invoice', 5))
  })

  it('shows result cards after successful search', async () => {
    vi.spyOn(api, 'searchDocuments').mockResolvedValue(mockSearchResponse)
    render(<SearchView />)

    await userEvent.type(screen.getByPlaceholderText('Search documents…'), 'invoice')
    await userEvent.click(screen.getByRole('button', { name: /search/i }))

    await waitFor(() => expect(screen.getByText('invoice.pdf')).toBeInTheDocument())
    expect(screen.queryByText('No results found.')).not.toBeInTheDocument()
  })

  it('shows "No results found" when search returns empty results', async () => {
    vi.spyOn(api, 'searchDocuments').mockResolvedValue({ query: 'xyz', top_n: 5, results: [] })
    render(<SearchView />)

    await userEvent.type(screen.getByPlaceholderText('Search documents…'), 'xyz')
    await userEvent.click(screen.getByRole('button', { name: /search/i }))

    await waitFor(() => expect(screen.getByText('No results found.')).toBeInTheDocument())
  })

  it('shows error message when search fails', async () => {
    vi.spyOn(api, 'searchDocuments').mockRejectedValue(new Error('Timeout'))
    render(<SearchView />)

    await userEvent.type(screen.getByPlaceholderText('Search documents…'), 'invoice')
    await userEvent.click(screen.getByRole('button', { name: /search/i }))

    await waitFor(() => expect(screen.getByText('Timeout')).toBeInTheDocument())
    expect(screen.queryByText('Searching…')).not.toBeInTheDocument()
  })
})
