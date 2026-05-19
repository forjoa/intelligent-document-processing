import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { UploadView } from '../components/UploadView'
import * as api from '../api'
import type { DocumentResponse } from '../types'

const mockDoc: DocumentResponse = {
  document_id: 'doc-42',
  filename: 'invoice.pdf',
  page_count: 3,
  document_type: 'invoice',
  classification_confidence: 0.92,
  fields: { vendor: 'Acme' },
  embedding_stored: true,
}

beforeEach(() => {
  vi.restoreAllMocks()
})

describe('UploadView', () => {
  it('rejects non-PDF files and shows error without calling fetch', async () => {
    const uploadSpy = vi.spyOn(api, 'uploadDocument')
    render(<UploadView />)

    const input = document.querySelector('input[type="file"]') as HTMLInputElement
    const txtFile = new File(['hello'], 'notes.txt', { type: 'text/plain' })

    // applyAccept: false lets the non-PDF file through to the component's own MIME check
    await userEvent.upload(input, txtFile, { applyAccept: false })

    expect(await screen.findByText('Only PDF files are accepted.')).toBeInTheDocument()
    expect(uploadSpy).not.toHaveBeenCalled()
  })

  it('shows spinner while upload is in progress', async () => {
    let resolveUpload!: (value: DocumentResponse) => void
    vi.spyOn(api, 'uploadDocument').mockReturnValue(
      new Promise<DocumentResponse>((res) => { resolveUpload = res }),
    )

    render(<UploadView />)

    const input = document.querySelector('input[type="file"]') as HTMLInputElement
    const pdfFile = new File(['%PDF-1.4'], 'invoice.pdf', { type: 'application/pdf' })

    await userEvent.upload(input, pdfFile)

    expect(screen.getByText('Processing document…')).toBeInTheDocument()

    resolveUpload(mockDoc)
    await waitFor(() => expect(screen.queryByText('Processing document…')).not.toBeInTheDocument())
  })

  it('shows DocumentCard with filename after successful upload', async () => {
    vi.spyOn(api, 'uploadDocument').mockResolvedValue(mockDoc)

    render(<UploadView />)

    const input = document.querySelector('input[type="file"]') as HTMLInputElement
    const pdfFile = new File(['%PDF-1.4'], 'invoice.pdf', { type: 'application/pdf' })

    await userEvent.upload(input, pdfFile)

    await waitFor(() => expect(screen.getByText('invoice.pdf')).toBeInTheDocument())
    expect(screen.queryByText('Processing document…')).not.toBeInTheDocument()
  })

  it('shows error message when upload fails', async () => {
    vi.spyOn(api, 'uploadDocument').mockRejectedValue(new Error('Server error'))

    render(<UploadView />)

    const input = document.querySelector('input[type="file"]') as HTMLInputElement
    const pdfFile = new File(['%PDF-1.4'], 'invoice.pdf', { type: 'application/pdf' })

    await userEvent.upload(input, pdfFile)

    await waitFor(() => expect(screen.getByText('Server error')).toBeInTheDocument())
    expect(screen.queryByText('Processing document…')).not.toBeInTheDocument()
  })
})
