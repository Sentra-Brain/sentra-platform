// src/features/chat/steps/StepPanel.tsx
import { ChevronDown, ChevronRight, CheckCircle, XCircle, Loader2, Search } from 'lucide-react'
import classNames from 'classnames'
import type { StepEntry } from './stepsSlice'

interface StepPanelProps {
  entry: StepEntry
  onToggle: (isOpen: boolean) => void
}

export default function StepPanel({ entry, onToggle }: StepPanelProps) {
  const formatDuration = (startedAt?: number, endedAt?: number) => {
    if (!startedAt) return null
    const end = endedAt || Date.now()
    const duration = end - startedAt
    if (duration < 1000) return `${duration}ms`
    if (duration < 60000) return `${(duration / 1000).toFixed(1)}s`
    return `${(duration / 60000).toFixed(1)}m`
  }

  const getStatusIcon = () => {
    switch (entry.status) {
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-600" />
      case 'error':
        return <XCircle className="w-4 h-4 text-red-600" />
      case 'searching':
        return <Search className="w-4 h-4 text-blue-600 animate-pulse" />
      case 'running':
      default:
        return <Loader2 className="w-4 h-4 text-blue-600 animate-spin" />
    }
  }

  const getStatusColor = () => {
    switch (entry.status) {
      case 'completed':
        return 'border-green-200 bg-green-50'
      case 'error':
        return 'border-red-200 bg-red-50'
      case 'searching':
        return 'border-blue-200 bg-blue-50'
      case 'running':
      default:
        return 'border-blue-200 bg-blue-50'
    }
  }

  const duration = formatDuration(entry.startedAt, entry.endedAt)
  
  return (
    <div className={classNames(
      'border rounded-lg overflow-hidden transition-all duration-200',
      getStatusColor()
    )}>
      {/* Header */}
      <button
        onClick={() => onToggle(!entry.isOpen)}
        className="w-full flex items-center justify-between p-3 hover:bg-black/5 transition-colors"
      >
        <div className="flex items-center gap-2">
          {getStatusIcon()}
          <span className="font-medium text-sm">
            {entry.label || entry.taskType || 'Step'}
          </span>
          {duration && (
            <span className="text-xs text-gray-500">
              ({duration})
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          {entry.progress !== undefined && (
            <div className="w-12 h-1.5 bg-white/50 rounded-full overflow-hidden">
              <div 
                className="h-full bg-current transition-all duration-300"
                style={{ width: `${Math.round(entry.progress * 100)}%` }}
              />
            </div>
          )}
          {entry.isOpen ? (
            <ChevronDown className="w-4 h-4 text-gray-500" />
          ) : (
            <ChevronRight className="w-4 h-4 text-gray-500" />
          )}
        </div>
      </button>

      {/* Body */}
      {entry.isOpen && (
        <div className="p-3 pt-0 border-t border-black/10">
          {entry.details && (
            <div className="text-sm text-gray-700 mb-2">
              {entry.details}
            </div>
          )}
          
          {entry.progress !== undefined && (
            <div className="mb-2">
              <div className="flex items-center justify-between text-xs text-gray-500 mb-1">
                <span>Progress</span>
                <span>{Math.round(entry.progress * 100)}%</span>
              </div>
              <div className="w-full h-2 bg-white/50 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-current transition-all duration-300"
                  style={{ width: `${Math.round(entry.progress * 100)}%` }}
                />
              </div>
            </div>
          )}

          {entry.meta && Object.keys(entry.meta).length > 0 && (
            <div className="mt-2">
              <div className="text-xs text-gray-500 mb-1">Details</div>
              <div className="space-y-1">
                {Object.entries(entry.meta).map(([key, value]) => {
                  // Show key metadata in a readable format
                  if (key === 'chunks_found' && typeof value === 'number') {
                    return (
                      <div key={key} className="text-xs text-gray-600">
                        Found {value} relevant chunks
                      </div>
                    )
                  }
                  if (key === 'source_ids' && Array.isArray(value) && value.length > 0) {
                    return (
                      <div key={key} className="text-xs text-gray-600">
                        Sources: {value.length} selected
                      </div>
                    )
                  }
                  if (key === 'document_ids' && Array.isArray(value) && value.length > 0) {
                    return (
                      <div key={key} className="text-xs text-gray-600">
                        Documents: {value.length} selected
                      </div>
                    )
                  }
                  // For other metadata, show as key: value if it's simple
                  if (typeof value === 'string' || typeof value === 'number') {
                    return (
                      <div key={key} className="text-xs text-gray-600">
                        {key}: {String(value)}
                      </div>
                    )
                  }
                  return null
                })}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}