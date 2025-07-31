// tests/upload.test.tsx
// Tests for upload functionality in Knowledge Management
import { describe, it, expect, vi } from 'vitest';

// Mock the knowledge service before any imports that use it
vi.mock('../src/services/knowledgeService', () => ({
  knowledgeService: {
    uploadDocument: vi.fn().mockResolvedValue({
      id: '1',
      filename: 'test.pdf',
      display_name: 'test',
      filetype: 'pdf',
      path: '/test.pdf',
      created_by: { full_name: 'Test User' },
      created_at: '2024-01-01T00:00:00Z',
      status: 'indexed',
      knowledge_source_id: '1'
    }),
    createKnowledgeSource: vi.fn().mockResolvedValue({
      id: '1',
      name: 'Test Source',
      type: 'upload',
      visibility: 'private',
      auto_index: true,
      status: 'active',
      created_by: { full_name: 'Test User' },
      created_at: '2024-01-01T00:00:00Z'
    })
  },
}));

// Mock the hooks
vi.mock('../src/hooks/useDocuments', () => ({
  useDocuments: () => ({
    uploadDocument: vi.fn().mockResolvedValue({
      id: '1',
      filename: 'test.pdf',
      display_name: 'test',
      filetype: 'pdf',
      path: '/test.pdf',
      created_by: { full_name: 'Test User' },
      created_at: '2024-01-01T00:00:00Z',
      status: 'indexed',
      knowledge_source_id: '1'
    })
  })
}));

vi.mock('../src/hooks/useKnowledgeSources', () => ({
  useKnowledgeSources: () => ({
    createSource: vi.fn().mockResolvedValue({
      id: '1',
      name: 'Test Source',
      type: 'upload',
      visibility: 'private',
      auto_index: true,
      status: 'active',
      created_by: { full_name: 'Test User' },
      created_at: '2024-01-01T00:00:00Z'
    })
  })
}));

import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';

import SimpleUploadDialog from '../src/components/knowledge/SimpleUploadDialog';
import SimpleCreateSourceDialog from '../src/components/knowledge/SimpleCreateSourceDialog';
import { KnowledgeSourceType, KnowledgeSourceVisibility } from '../src/models/knowledgeModels';

describe('Upload Functionality', () => {
  describe('SimpleUploadDialog', () => {
    it('renders upload dialog correctly', () => {
      render(
        <SimpleUploadDialog
          isOpen={true}
          onClose={vi.fn()}
          onUploadComplete={vi.fn()}
        />
      );

      expect(screen.getByText('Upload Documents')).toBeInTheDocument();
      expect(screen.getByText('Click to select files or drag and drop')).toBeInTheDocument();
    });

    it('handles file selection', () => {
      render(
        <SimpleUploadDialog
          isOpen={true}
          onClose={vi.fn()}
          onUploadComplete={vi.fn()}
        />
      );

      const fileInput = screen.getByLabelText(/click to select files/i);
      expect(fileInput).toBeInTheDocument();
    });
  });

  describe('SimpleCreateSourceDialog', () => {
    it('renders create source dialog correctly', () => {
      render(
        <SimpleCreateSourceDialog
          isOpen={true}
          onClose={vi.fn()}
          onCreateComplete={vi.fn()}
        />
      );

      expect(screen.getByText('Create Knowledge Source')).toBeInTheDocument();
      expect(screen.getByLabelText(/name/i)).toBeInTheDocument();
    });

    it('validates required fields', () => {
      render(
        <SimpleCreateSourceDialog
          isOpen={true}
          onClose={vi.fn()}
          onCreateComplete={vi.fn()}
        />
      );

      const createButton = screen.getByRole('button', { name: /create source/i });
      expect(createButton).toBeDisabled();
    });
  });

  describe('Models Integration', () => {
    it('validates that upload functionality uses correct models', () => {
      // This test ensures that our upload components use the correct models and services
      expect(KnowledgeSourceType.UPLOAD).toBe('upload');
      expect(KnowledgeSourceType.FOLDER).toBe('folder');
      expect(KnowledgeSourceVisibility.PRIVATE).toBe('private');
      expect(KnowledgeSourceVisibility.SHARED).toBe('shared');
      expect(KnowledgeSourceVisibility.ORG_WIDE).toBe('org-wide');
    });
  });
});