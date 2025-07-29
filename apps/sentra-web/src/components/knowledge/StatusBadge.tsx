// src/components/knowledge/StatusBadge.tsx
// Status badge component for documents and knowledge sources
import React from 'react';
import type { DocumentStatus, KnowledgeSourceStatus } from '../../models/knowledgeModels';
import { DocumentStatus as DocStatus, KnowledgeSourceStatus as KSStatus } from '../../models/knowledgeModels';

interface StatusBadgeProps {
  status: DocumentStatus | KnowledgeSourceStatus;
  className?: string;
}

const StatusBadge: React.FC<StatusBadgeProps> = ({ status, className = '' }) => {
  const getStatusConfig = (status: DocumentStatus | KnowledgeSourceStatus) => {
    switch (status) {
      case DocStatus.INDEXED:
      case KSStatus.ACTIVE:
        return {
          icon: '✅',
          text: status === DocStatus.INDEXED ? 'Indexed' : 'Active',
          style: 'status-badge-success',
        };
      case DocStatus.PROCESSING:
        return {
          icon: '⏳',
          text: 'Processing',
          style: 'status-badge-warning',
        };
      case DocStatus.QUEUED:
        return {
          icon: '⏸️',
          text: 'Queued',
          style: 'status-badge-info',
        };
      case DocStatus.FAILED:
      case KSStatus.ERROR:
        return {
          icon: '❌',
          text: 'Failed',
          style: 'status-badge-error',
        };
      case DocStatus.TO_BE_REMOVED:
        return {
          icon: '🗑️',
          text: 'To be removed',
          style: 'status-badge-warning',
        };
      case KSStatus.DISABLED:
        return {
          icon: '🛑',
          text: 'Disabled',
          style: 'status-badge-disabled',
        };
      default:
        return {
          icon: '❓',
          text: status,
          style: 'status-badge-default',
        };
    }
  };

  const config = getStatusConfig(status);

  return (
    <span className={`status-badge ${config.style} ${className}`}>
      <span className="status-badge-icon">{config.icon}</span>
      <span className="status-badge-text">{config.text}</span>
    </span>
  );
};

export default StatusBadge;