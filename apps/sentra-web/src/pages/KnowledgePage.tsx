// src/pages/KnowledgePage.tsx
// Main Knowledge Management page with master-detail layout
import React, { useState } from 'react';
import KnowledgeTreeView from '../components/knowledge/KnowledgeTreeView';
import KnowledgeDetailPanel from '../components/knowledge/KnowledgeDetailPanel';
import type { KnowledgeTreeNode } from '../models/knowledgeModels';

const KnowledgePage: React.FC = () => {
  const [selectedNode, setSelectedNode] = useState<KnowledgeTreeNode | undefined>();

  const handleSelectNode = (node: KnowledgeTreeNode) => {
    setSelectedNode(node);
  };

  return (
    <div className="h-full flex">
      {/* Master Panel - Tree View */}
      <div className="w-1/3 min-w-80 border-r bg-white">
        <KnowledgeTreeView
          onSelectNode={handleSelectNode}
          selectedNodeId={selectedNode?.id}
        />
      </div>

      {/* Detail Panel */}
      <div className="flex-1 bg-white">
        <KnowledgeDetailPanel selectedNode={selectedNode} />
      </div>
    </div>
  );
};

export default KnowledgePage;