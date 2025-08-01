// src/pages/KnowledgePage.tsx
// Main Knowledge Management page with routing
import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useKnowledgeNavigation } from '../hooks/useKnowledgeNavigation';
import { useKnowledgeSources } from '../hooks/useKnowledgeSources';
import { knowledgeService } from '../services/knowledgeService';
import { KnowledgeSourceType, KnowledgeSourceVisibility } from '../models/knowledgeModels';
import { notifyError } from '../lib/notify';
import KnowledgeSourcesList from '../components/knowledge/KnowledgeSourcesList';
import KnowledgeSourceDetail from '../components/knowledge/KnowledgeSourceDetail';
import DocumentDetail from '../components/knowledge/DocumentDetail';
import SimpleUploadDialog from '../components/knowledge/SimpleUploadDialog';
import SimpleCreateSourceDialog from '../components/knowledge/SimpleCreateSourceDialog';

const KnowledgePage: React.FC = () => {
  const { sourceId, documentId } = useParams();
  const { getCurrentSourceId, getCurrentDocumentId } = useKnowledgeNavigation();
  const { sources } = useKnowledgeSources();
  
  const [showUploadDialog, setShowUploadDialog] = useState(false);
  const [showCreateSourceDialog, setShowCreateSourceDialog] = useState(false);
  const [uploadSourceId, setUploadSourceId] = useState<string | null>(null);
  
  const currentSourceId = sourceId || getCurrentSourceId();
  const currentDocumentId = documentId || getCurrentDocumentId();

  const handleDialogClose = () => {
    setShowUploadDialog(false);
    setShowCreateSourceDialog(false);
    setUploadSourceId(null);
  };

  // Find or create an upload source for general uploads
  const getOrCreateUploadSource = async (): Promise<string> => {
    // Look for existing upload source
    const existingUploadSource = sources.find(source => source.type === KnowledgeSourceType.UPLOAD);
    if (existingUploadSource) {
      return existingUploadSource.id;
    }

    // Create a new upload source
    try {
      const newSource = await knowledgeService.createKnowledgeSource({
        name: 'File Uploads',
        type: KnowledgeSourceType.UPLOAD,
        description: 'Documents uploaded through the web interface',
        visibility: KnowledgeSourceVisibility.PRIVATE,
        auto_index: true,
      });
      return newSource.id;
    } catch (error) {
      notifyError(`Failed to create upload source: ${error}`);
      throw error;
    }
  };

  const handleUploadFromList = async () => {
    try {
      const sourceId = await getOrCreateUploadSource();
      setUploadSourceId(sourceId);
      setShowUploadDialog(true);
    } catch (error) {
      // Error already notified in getOrCreateUploadSource
    }
  };

  const handleUploadFromSource = (sourceId: string) => {
    setUploadSourceId(sourceId);
    setShowUploadDialog(true);
  };

  // Document detail view
  if (currentDocumentId) {
    return (
      <>
        <DocumentDetail documentId={currentDocumentId} />
        
        {uploadSourceId && (
          <SimpleUploadDialog
            isOpen={showUploadDialog}
            onClose={handleDialogClose}
            onUploadComplete={handleDialogClose}
            knowledgeSourceId={uploadSourceId}
          />
        )}
      </>
    );
  }

  // Knowledge source detail view
  if (currentSourceId) {
    return (
      <>
        <KnowledgeSourceDetail 
          sourceId={currentSourceId}
          onUpload={() => handleUploadFromSource(currentSourceId)}
        />
        
        {uploadSourceId && (
          <SimpleUploadDialog
            isOpen={showUploadDialog}
            onClose={handleDialogClose}
            onUploadComplete={handleDialogClose}
            knowledgeSourceId={uploadSourceId}
          />
        )}
        
        <SimpleCreateSourceDialog
          isOpen={showCreateSourceDialog}
          onClose={handleDialogClose}
          onCreateComplete={handleDialogClose}
        />
      </>
    );
  }

  // Default: Knowledge sources list view
  return (
    <>
      <KnowledgeSourcesList
        onCreateSource={() => setShowCreateSourceDialog(true)}
        onUpload={handleUploadFromList}
      />
      
      {uploadSourceId && (
        <SimpleUploadDialog
          isOpen={showUploadDialog}
          onClose={handleDialogClose}
          onUploadComplete={handleDialogClose}
          knowledgeSourceId={uploadSourceId}
        />
      )}
      
      <SimpleCreateSourceDialog
        isOpen={showCreateSourceDialog}
        onClose={handleDialogClose}
        onCreateComplete={handleDialogClose}
      />
    </>
  );
};

export default KnowledgePage;