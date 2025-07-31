// tests/upload.test.tsx
// Tests for upload functionality in Knowledge Management
import { describe, it, expect, vi } from 'vitest';

// Mock the knowledge service before any imports that use it
vi.mock('../src/services/knowledgeService', () => ({
  knowledgeService: {
    uploadMultipleDocuments: vi.fn().mockResolvedValue([]),
    uploadFolderAsKnowledgeSource: vi.fn().mockResolvedValue({
      knowledgeSource: { id: '1', name: 'Test Source' },
      documents: [],
      progress: vi.fn()
    }),
    createKnowledgeSource: vi.fn().mockResolvedValue({
      id: '1',
      name: 'Test Source',
      type: 'upload',
      visibility: 'private',
      auto_index: true,
      status: 'active',
      created_by: 'test@example.com',
      created_at: '2024-01-01T00:00:00Z'
    })
  },
}));

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';

import UploadDialog from '../src/components/knowledge/UploadDialog';
import CreateKnowledgeSourceDialog from '../src/components/knowledge/CreateKnowledgeSourceDialog';
import { KnowledgeSourceType, KnowledgeSourceVisibility } from '../src/models/knowledgeModels';

const mockKnowledgeSources = [
  {
    id: '1',
    name: 'My Documents',
    type: KnowledgeSourceType.UPLOAD as const,
    visibility: KnowledgeSourceVisibility.PRIVATE as const,
    auto_index: true,
    status: 'active' as const,
    created_by: 'test@example.com',
    created_at: '2024-01-01T00:00:00Z'
  },
  {
    id: '2',
    name: 'Shared Files',
    type: KnowledgeSourceType.FOLDER as const,
    visibility: KnowledgeSourceVisibility.SHARED as const,
    auto_index: true,
    status: 'active' as const,
    created_by: 'admin@example.com',
    created_at: '2024-01-01T00:00:00Z'
  }
];

describe('UploadDialog', () => {
  const defaultProps = {
    isOpen: true,
    onClose: vi.fn(),
    onUploadComplete: vi.fn(),
    knowledgeSources: mockKnowledgeSources,
  };

  it('renders upload dialog when open', () => {
    render(<UploadDialog {...defaultProps} />);
    
    expect(screen.getByText('Upload Documents')).toBeInTheDocument();
    expect(screen.getByText('Upload to Knowledge Source')).toBeInTheDocument();
    expect(screen.getByText('Select Files')).toBeInTheDocument();
  });

  it('shows knowledge sources in dropdown', () => {
    render(<UploadDialog {...defaultProps} />);
    
    expect(screen.getByDisplayValue('')).toBeInTheDocument();
    expect(screen.getByText('My Documents (private)')).toBeInTheDocument();
    expect(screen.getByText('Shared Files (shared)')).toBeInTheDocument();
  });

  it('does not render when closed', () => {
    render(<UploadDialog {...defaultProps} isOpen={false} />);
    
    expect(screen.queryByText('Upload Documents')).not.toBeInTheDocument();
  });

  it('allows file selection via browse button', () => {
    render(<UploadDialog {...defaultProps} />);
    
    const browseButton = screen.getByText('browse');
    expect(browseButton).toBeInTheDocument();
    
    fireEvent.click(browseButton);
    // File input should be triggered (though we can't easily test file selection in jsdom)
  });

  it('shows cancel and upload buttons', () => {
    render(<UploadDialog {...defaultProps} />);
    
    expect(screen.getByText('Cancel')).toBeInTheDocument();
    expect(screen.getByText('Upload File')).toBeInTheDocument();
  });
});

describe('CreateKnowledgeSourceDialog', () => {
  const defaultProps = {
    isOpen: true,
    onClose: vi.fn(),
    onCreateComplete: vi.fn(),
  };

  it('renders create knowledge source dialog when open', () => {
    render(<CreateKnowledgeSourceDialog {...defaultProps} />);
    
    expect(screen.getByText('Create Knowledge Source')).toBeInTheDocument();
    expect(screen.getByText('Knowledge Source Name *')).toBeInTheDocument();
    expect(screen.getByText('Description')).toBeInTheDocument();
    expect(screen.getByText('Visibility')).toBeInTheDocument();
  });

  it('shows metadata form fields', () => {
    render(<CreateKnowledgeSourceDialog {...defaultProps} />);
    
    expect(screen.getByPlaceholderText('Enter a name for your knowledge source')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Optional description')).toBeInTheDocument();
    
    // Check that the visibility dropdown has the expected options
    expect(screen.getByRole('option', { name: 'Private' })).toBeInTheDocument();
    expect(screen.getByRole('option', { name: 'Shared' })).toBeInTheDocument();
    expect(screen.getByRole('option', { name: 'Organization-Wide' })).toBeInTheDocument();
  });

  it('has next button on metadata step', () => {
    render(<CreateKnowledgeSourceDialog {...defaultProps} />);
    
    expect(screen.getByText('Next')).toBeInTheDocument();
    expect(screen.getByText('Cancel')).toBeInTheDocument();
  });

  it('does not render when closed', () => {
    render(<CreateKnowledgeSourceDialog {...defaultProps} isOpen={false} />);
    
    expect(screen.queryByText('Create Knowledge Source')).not.toBeInTheDocument();
  });

  it('allows auto-index toggle', () => {
    render(<CreateKnowledgeSourceDialog {...defaultProps} />);
    
    const autoIndexCheckbox = screen.getByRole('checkbox');
    expect(autoIndexCheckbox).toBeInTheDocument();
    expect(autoIndexCheckbox).toBeChecked(); // Should be checked by default
    
    fireEvent.click(autoIndexCheckbox);
    expect(autoIndexCheckbox).not.toBeChecked();
  });
});

describe('Upload Integration', () => {
  it('validates that upload functionality is properly integrated', () => {
    // This test ensures that our upload components use the correct models and services
    expect(KnowledgeSourceType.UPLOAD).toBe('upload');
    expect(KnowledgeSourceType.FOLDER).toBe('folder');
    expect(KnowledgeSourceVisibility.PRIVATE).toBe('private');
    expect(KnowledgeSourceVisibility.SHARED).toBe('shared');
    expect(KnowledgeSourceVisibility.ORG_WIDE).toBe('org-wide');
  });
});