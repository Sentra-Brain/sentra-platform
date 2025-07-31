// src/pages/KnowledgePage.tsx
// Main Knowledge Management page with routing
import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useKnowledgeNavigation } from '../hooks/useKnowledgeNavigation';
import KnowledgeSourcesList from '../components/knowledge/KnowledgeSourcesList';
import KnowledgeSourceDetail from '../components/knowledge/KnowledgeSourceDetail';
import DocumentDetail from '../components/knowledge/DocumentDetail';
import SimpleUploadDialog from '../components/knowledge/SimpleUploadDialog';
import SimpleCreateSourceDialog from '../components/knowledge/SimpleCreateSourceDialog';

const KnowledgePage: React.FC = () => {
  const { sourceId, documentId } = useParams();
  const { getCurrentSourceId, getCurrentDocumentId } = useKnowledgeNavigation();
  
  const [showUploadDialog, setShowUploadDialog] = useState(false);
  const [showCreateSourceDialog, setShowCreateSourceDialog] = useState(false);
  
  const currentSourceId = sourceId || getCurrentSourceId();
  const currentDocumentId = documentId || getCurrentDocumentId();

  const handleDialogClose = () => {
    setShowUploadDialog(false);
    setShowCreateSourceDialog(false);
  };

  // Document detail view
  if (currentDocumentId) {
    return (
      <>
        <DocumentDetail documentId={currentDocumentId} />
        
        <SimpleUploadDialog
          isOpen={showUploadDialog}
          onClose={handleDialogClose}
          onUploadComplete={handleDialogClose}
        />
      </>
    );
  }

  // Knowledge source detail view
  if (currentSourceId) {
    return (
      <>
        <KnowledgeSourceDetail 
          sourceId={currentSourceId}
          onUpload={() => setShowUploadDialog(true)}
        />
        
        <SimpleUploadDialog
          isOpen={showUploadDialog}
          onClose={handleDialogClose}
          onUploadComplete={handleDialogClose}
        />
        
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
        onUpload={() => setShowUploadDialog(true)}
      />
      
      <SimpleUploadDialog
        isOpen={showUploadDialog}
        onClose={handleDialogClose}
        onUploadComplete={handleDialogClose}
      />
      
      <SimpleCreateSourceDialog
        isOpen={showCreateSourceDialog}
        onClose={handleDialogClose}
        onCreateComplete={handleDialogClose}
      />
    </>
  );
};

export default KnowledgePage;