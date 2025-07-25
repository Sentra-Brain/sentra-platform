// src/pages/KnowledgeDemoPage.tsx
// Demo page to showcase upload functionality without authentication
import React, { useState } from 'react';
import UploadDialog from '../components/knowledge/UploadDialog';
import CreateKnowledgeSourceDialog from '../components/knowledge/CreateKnowledgeSourceDialog';
import { KnowledgeSourceType, KnowledgeSourceVisibility } from '../models/knowledgeModels';
import type { KnowledgeSource } from '../models/knowledgeModels';

const mockKnowledgeSources: KnowledgeSource[] = [
  {
    id: '1',
    name: 'My Personal Documents',
    type: KnowledgeSourceType.UPLOAD,
    visibility: KnowledgeSourceVisibility.PRIVATE,
    auto_index: true,
    status: 'active',
    created_by: 'demo@example.com',
    created_at: '2024-01-15T10:30:00Z',
    description: 'Personal document collection'
  },
  {
    id: '2', 
    name: 'Team Shared Resources',
    type: KnowledgeSourceType.FOLDER,
    visibility: KnowledgeSourceVisibility.SHARED,
    auto_index: true,
    status: 'active',
    created_by: 'admin@example.com',
    created_at: '2024-01-10T09:00:00Z',
    path: '/shared/team-docs',
    description: 'Shared team documentation and resources'
  },
  {
    id: '3',
    name: 'Company Knowledge Base',
    type: KnowledgeSourceType.FOLDER,
    visibility: KnowledgeSourceVisibility.ORG_WIDE,
    auto_index: true,
    status: 'active',
    created_by: 'admin@example.com',
    created_at: '2024-01-01T00:00:00Z',
    path: '/company/knowledge',
    description: 'Organization-wide knowledge base and policies'
  }
];

const KnowledgeDemoPage: React.FC = () => {
  const [showUploadDialog, setShowUploadDialog] = useState(false);
  const [showCreateSourceDialog, setShowCreateSourceDialog] = useState(false);

  const handleUploadComplete = () => {
    console.log('Upload completed!');
  };

  const handleCreateSourceComplete = () => {
    console.log('Knowledge source created!');
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="rounded-lg shadow-md p-6 mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Knowledge Management Demo
          </h1>
          <p className="text-gray-600 mb-6">
            This demo showcases the upload functionality implemented in Steps 2 & 3
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="border border-gray-200 rounded-lg p-4">
              <h2 className="text-xl font-semibold mb-3">Step 2: Upload Documents</h2>
              <p className="text-gray-600 mb-4">
                Upload documents to existing knowledge sources with support for:
              </p>
              <ul className="text-sm text-gray-600 mb-4 space-y-1">
                <li>• Multiple file selection</li>
                <li>• Drag and drop support</li>
                <li>• Target knowledge source selection</li>
                <li>• Upload permission filtering</li>
              </ul>
              <button
                onClick={() => setShowUploadDialog(true)}
                className="w-full bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
              >
                Demo Upload Documents
              </button>
            </div>

            <div className="border border-gray-200 rounded-lg p-4">
              <h2 className="text-xl font-semibold mb-3">Step 3: Create Knowledge Source</h2>
              <p className="text-gray-600 mb-4">
                Create new knowledge sources from folder uploads with:
              </p>
              <ul className="text-sm text-gray-600 mb-4 space-y-1">
                <li>• Multi-step creation wizard</li>
                <li>• Folder or file selection</li>
                <li>• Metadata configuration</li>
                <li>• Progress tracking</li>
              </ul>
              <button
                onClick={() => setShowCreateSourceDialog(true)}
                className="w-full bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 transition-colors"
              >
                Demo Create Knowledge Source
              </button>
            </div>
          </div>
        </div>

        <div className="rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">Available Knowledge Sources</h2>
          <div className="space-y-3">
            {mockKnowledgeSources.map((source) => (
              <div key={source.id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h3 className="font-medium text-gray-900">{source.name}</h3>
                    <p className="text-sm text-gray-600 mt-1">{source.description}</p>
                    <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                      <span className="capitalize">Type: {source.type}</span>
                      <span className="capitalize">Visibility: {source.visibility}</span>
                      <span>Auto-index: {source.auto_index ? 'Yes' : 'No'}</span>
                    </div>
                    {source.path && (
                      <div className="mt-2">
                        <code className="text-xs bg-gray-100 px-2 py-1 rounded">{source.path}</code>
                      </div>
                    )}
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                      {source.status}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Upload Dialog */}
      <UploadDialog
        isOpen={showUploadDialog}
        onClose={() => setShowUploadDialog(false)}
        onUploadComplete={handleUploadComplete}
        knowledgeSources={mockKnowledgeSources}
        defaultKnowledgeSourceId={mockKnowledgeSources[0].id}
      />

      {/* Create Knowledge Source Dialog */}
      <CreateKnowledgeSourceDialog
        isOpen={showCreateSourceDialog}
        onClose={() => setShowCreateSourceDialog(false)}
        onCreateComplete={handleCreateSourceComplete}
      />
    </div>
  );
};

export default KnowledgeDemoPage;