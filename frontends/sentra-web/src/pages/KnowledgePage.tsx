// src/pages/KnowledgePage.tsx
// Main Knowledge Management page with master-detail layout
import React from 'react';
import KnowledgeTreeView from '../components/knowledge/KnowledgeTreeView';
import KnowledgeDetailPanel from '../components/knowledge/KnowledgeDetailPanel';

const KnowledgePage: React.FC = () => {
  return (
    <div className="h-full flex">
      {/* Master Panel - Tree View */}
      <div className="w-1/3 min-w-80 border-r">
        <KnowledgeTreeView />
      </div>

      {/* Detail Panel */}
      <div className="flex-1">
        <KnowledgeDetailPanel />
      </div>
    </div>
  );
};

export default KnowledgePage;