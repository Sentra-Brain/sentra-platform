// tests/DocumentRow.test.tsx
// Test DocumentRow component functionality
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { vi } from 'vitest';
import DocumentRow from '../src/components/knowledge/DocumentRow';
import { knowledgeService } from '../src/services/knowledgeService';
import type { Document } from '../src/models/knowledgeModels';

// Mock the knowledge service
vi.mock('../src/services/knowledgeService', () => ({
  knowledgeService: {
    reindexDocument: vi.fn(),
    removeDocument: vi.fn(),
  },
}));

// Mock the notify functions
vi.mock('../src/lib/notify', () => ({
  notifySuccess: vi.fn(),
  notifyError: vi.fn(),
}));

const mockDocument: Document = {
  id: 'doc-1',
  filename: 'test-document.pdf',
  display_name: 'Test Document',
  description: 'A test document',
  filetype: 'pdf',
  path: '/path/to/document.pdf',
  uploaded_by: 'user-123',
  uploaded_at: '2023-12-01T10:00:00Z',
  status: 'indexed',
  knowledge_source_id: 'ks-1',
  chunks_count: 42,
};

describe('DocumentRow Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render document information correctly', () => {
    const onDocumentUpdated = vi.fn();
    const onDocumentClick = vi.fn();

    render(
      <DocumentRow
        document={mockDocument}
        onDocumentUpdated={onDocumentUpdated}
        onDocumentClick={onDocumentClick}
        userDisplayName="John Doe"
      />
    );

    expect(screen.getByText('Test Document')).toBeInTheDocument();
    expect(screen.getByText('test-document.pdf')).toBeInTheDocument();
    expect(screen.getByText('PDF')).toBeInTheDocument();
    expect(screen.getByText('by John Doe')).toBeInTheDocument();
    expect(screen.getByText('42 chunks')).toBeInTheDocument();
    expect(screen.getByText('Re-Index')).toBeInTheDocument();
    expect(screen.getByText('Remove')).toBeInTheDocument();
  });

  it('should handle re-index action', async () => {
    const updatedDocument = { ...mockDocument, status: 'pending' as const };
    vi.mocked(knowledgeService.reindexDocument).mockResolvedValue(updatedDocument);

    const onDocumentUpdated = vi.fn();
    const onDocumentClick = vi.fn();

    render(
      <DocumentRow
        document={mockDocument}
        onDocumentUpdated={onDocumentUpdated}
        onDocumentClick={onDocumentClick}
      />
    );

    const reindexButton = screen.getByText('Re-Index');
    fireEvent.click(reindexButton);

    await waitFor(() => {
      expect(knowledgeService.reindexDocument).toHaveBeenCalledWith('doc-1');
      expect(onDocumentUpdated).toHaveBeenCalledWith(updatedDocument);
    });
  });

  it('should handle remove action with confirmation', async () => {
    const updatedDocument = { ...mockDocument, status: 'to_be_removed' as const };
    vi.mocked(knowledgeService.removeDocument).mockResolvedValue(updatedDocument);

    // Mock window.confirm to return true
    global.confirm = vi.fn(() => true);

    const onDocumentUpdated = vi.fn();
    const onDocumentClick = vi.fn();

    render(
      <DocumentRow
        document={mockDocument}
        onDocumentUpdated={onDocumentUpdated}
        onDocumentClick={onDocumentClick}
      />
    );

    const removeButton = screen.getByText('Remove');
    fireEvent.click(removeButton);

    await waitFor(() => {
      expect(global.confirm).toHaveBeenCalledWith(
        'Are you sure you want to remove this document? This action cannot be undone.'
      );
      expect(knowledgeService.removeDocument).toHaveBeenCalledWith('doc-1');
      expect(onDocumentUpdated).toHaveBeenCalledWith(updatedDocument);
    });
  });

  it('should handle document click for navigation', () => {
    const onDocumentUpdated = vi.fn();
    const onDocumentClick = vi.fn();

    render(
      <DocumentRow
        document={mockDocument}
        onDocumentUpdated={onDocumentUpdated}
        onDocumentClick={onDocumentClick}
      />
    );

    const documentRow = screen.getByText('Test Document').closest('.document-row');
    fireEvent.click(documentRow!);

    expect(onDocumentClick).toHaveBeenCalledWith(mockDocument);
  });

  it('should disable remove button for documents marked for removal', () => {
    const documentToBeRemoved = { ...mockDocument, status: 'to_be_removed' as const };
    const onDocumentUpdated = vi.fn();

    render(
      <DocumentRow
        document={documentToBeRemoved}
        onDocumentUpdated={onDocumentUpdated}
      />
    );

    const removeButton = screen.getByText('Remove');
    expect(removeButton).toBeDisabled();
  });
});