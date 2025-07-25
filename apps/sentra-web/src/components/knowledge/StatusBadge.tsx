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
          bgColor: 'bg-green-100',
          textColor: 'text-green-800',
        };
      case DocStatus.PROCESSING:
        return {
          icon: '⏳',
          text: 'Processing',
          bgColor: 'bg-yellow-100',
          textColor: 'text-yellow-800',
        };
      case DocStatus.QUEUED:
        return {
          icon: '⏸️',
          text: 'Queued',
          bgColor: 'bg-blue-100',
          textColor: 'text-blue-800',
        };
      case DocStatus.FAILED:
      case KSStatus.ERROR:
        return {
          icon: '❌',
          text: 'Failed',
          bgColor: 'bg-red-100',
          textColor: 'text-red-800',
        };
      case KSStatus.DISABLED:
        return {
          icon: '🛑',
          text: 'Disabled',
          bgColor: 'bg-gray-100',
          textColor: 'text-gray-800',
        };
      default:
        return {
          icon: '❓',
          text: status,
          bgColor: 'bg-gray-100',
          textColor: 'text-gray-800',
        };
    }
  };

  const config = getStatusConfig(status);

  return (
    <span
      className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${config.bgColor} ${config.textColor} ${className}`}
    >
      <span>{config.icon}</span>
      <span>{config.text}</span>
    </span>
  );
};

export default StatusBadge;