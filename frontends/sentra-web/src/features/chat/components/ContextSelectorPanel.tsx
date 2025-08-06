import { useState, useEffect } from 'react';
import { X, Check, Folder, FileText } from 'lucide-react';
import { useAppSelector, useAppDispatch } from '@store/hooks';
import { 
  setSelectedContext, 
  type SelectedContext 
} from '../chatSlice';
import { 
  fetchSourcesWithDocuments, 
  setVisibility 
} from '@features/knowledge/knowledgeSlice';
import type { KnowledgeSourceVisibility } from '@features/knowledge/types/knowledgeModels';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  onApply: () => void;
}

export default function ContextSelectorPanel({ isOpen, onClose, onApply }: Props) {
  const dispatch = useAppDispatch();
  
  const { selectedContext } = useAppSelector(s => s.chat);
  const { 
    sources, 
    documentsBySource, 
    visibility, 
    sourcesLoading, 
    documentsLoading 
  } = useAppSelector(s => s.knowledge);

  // Local state for the selector
  const [localContext, setLocalContext] = useState<SelectedContext>(selectedContext);
  const [selectedVisibility, setSelectedVisibility] = useState<KnowledgeSourceVisibility>(visibility);

  useEffect(() => {
    if (isOpen) {
      setLocalContext(selectedContext);
      setSelectedVisibility(visibility);
    }
  }, [isOpen, selectedContext, visibility]);

  useEffect(() => {
    if (isOpen && selectedVisibility !== visibility) {
      dispatch(setVisibility(selectedVisibility));
      dispatch(fetchSourcesWithDocuments());
    }
  }, [dispatch, isOpen, selectedVisibility, visibility]);

  useEffect(() => {
    if (isOpen && !sources.length && !sourcesLoading) {
      dispatch(fetchSourcesWithDocuments());
    }
  }, [dispatch, isOpen, sources.length, sourcesLoading]);

  const handleVisibilityChange = (newVisibility: KnowledgeSourceVisibility) => {
    setSelectedVisibility(newVisibility);
  };

  const handleUseRagToggle = () => {
    setLocalContext(prev => ({ ...prev, useRag: !prev.useRag }));
  };

  const handleSourceToggle = (sourceId: string) => {
    setLocalContext(prev => {
      const isSelected = prev.sourceIds.includes(sourceId);
      let newSourceIds: string[];
      let newDocumentIds = [...prev.documentIds];

      if (isSelected) {
        // Remove source and all its documents
        newSourceIds = prev.sourceIds.filter(id => id !== sourceId);
        const sourceDocuments = documentsBySource[sourceId] || [];
        newDocumentIds = newDocumentIds.filter(
          docId => !sourceDocuments.some(doc => doc.id === docId)
        );
      } else {
        // Add source
        newSourceIds = [...prev.sourceIds, sourceId];
      }

      return {
        ...prev,
        sourceIds: newSourceIds,
        documentIds: newDocumentIds,
      };
    });
  };

  const handleDocumentToggle = (sourceId: string, documentId: string) => {
    setLocalContext(prev => {
      const isSelected = prev.documentIds.includes(documentId);
      let newDocumentIds: string[];
      let newSourceIds = [...prev.sourceIds];

      if (isSelected) {
        // Remove document
        newDocumentIds = prev.documentIds.filter(id => id !== documentId);
      } else {
        // Add document and ensure source is also selected
        newDocumentIds = [...prev.documentIds, documentId];
        if (!newSourceIds.includes(sourceId)) {
          newSourceIds.push(sourceId);
        }
      }

      return {
        ...prev,
        sourceIds: newSourceIds,
        documentIds: newDocumentIds,
      };
    });
  };

  const handleApply = () => {
    dispatch(setSelectedContext(localContext));
    onApply();
  };

  const handleCancel = () => {
    setLocalContext(selectedContext);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-[var(--sentra-primary-dark)] border border-[var(--sentra-accent-light)] rounded-lg shadow-lg max-w-md w-full mx-4 max-h-[80vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-[var(--sentra-accent-light)]">
          <h3 className="text-lg font-medium text-[var(--sentra-text)]">📚 Select Context</h3>
          <button
            onClick={handleCancel}
            className="p-1 hover:bg-[var(--sentra-accent-light)] rounded transition-colors"
          >
            <X size={20} className="text-[var(--sentra-muted)]" />
          </button>
        </div>

        {/* Content */}
        <div className="p-4 overflow-y-auto max-h-[60vh]">
          {/* Use RAG Toggle */}
          <div className="mb-4">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={localContext.useRag}
                onChange={handleUseRagToggle}
                className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
              />
              <span className="text-[var(--sentra-text)]">Use Context Knowledge</span>
            </label>
            <p className="text-sm text-[var(--sentra-muted)] mt-1">
              When enabled, selected sources and documents will be used for context
            </p>
          </div>

          {localContext.useRag && (
            <>
              {/* Visibility Selection */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-[var(--sentra-text)] mb-2">
                  Visibility
                </label>
                <div className="flex gap-2">
                  {(['private', 'shared', 'org-wide'] as KnowledgeSourceVisibility[]).map((vis) => (
                    <button
                      key={vis}
                      onClick={() => handleVisibilityChange(vis)}
                      className={`px-3 py-1 rounded text-sm transition-colors ${
                        selectedVisibility === vis
                          ? 'bg-blue-600 text-white'
                          : 'bg-[var(--sentra-accent-light)] text-[var(--sentra-text)] hover:bg-[var(--sentra-accent)]'
                      }`}
                    >
                      {vis}
                    </button>
                  ))}
                </div>
              </div>

              {/* Loading State */}
              {(sourcesLoading || documentsLoading) && (
                <div className="text-center py-4">
                  <div className="text-[var(--sentra-muted)]">Loading sources...</div>
                </div>
              )}

              {/* Sources and Documents */}
              {!sourcesLoading && !documentsLoading && (
                <div className="space-y-3">
                  {sources.length === 0 ? (
                    <div className="text-center py-4 text-[var(--sentra-muted)]">
                      No sources found for {selectedVisibility} visibility
                    </div>
                  ) : (
                    sources.map((source) => {
                      const sourceDocuments = documentsBySource[source.id] || [];
                      const isSourceSelected = localContext.sourceIds.includes(source.id);
                      
                      return (
                        <div key={source.id} className="space-y-2">
                          {/* Source */}
                          <div 
                            className="flex items-center gap-2 p-2 rounded hover:bg-[var(--sentra-accent-light)] cursor-pointer"
                            onClick={() => handleSourceToggle(source.id)}
                          >
                            <div className="w-4 h-4 flex items-center justify-center">
                              {isSourceSelected && <Check size={14} className="text-green-500" />}
                            </div>
                            <Folder size={16} className="text-blue-400" />
                            <span className="text-[var(--sentra-text)] flex-1">{source.name}</span>
                            <span className="text-xs text-[var(--sentra-muted)]">
                              {sourceDocuments.length} docs
                            </span>
                          </div>

                          {/* Documents */}
                          {isSourceSelected && sourceDocuments.length > 0 && (
                            <div className="ml-6 space-y-1">
                              {sourceDocuments.map((doc) => {
                                const isDocSelected = localContext.documentIds.includes(doc.id);
                                
                                return (
                                  <div
                                    key={doc.id}
                                    className="flex items-center gap-2 p-1 rounded hover:bg-[var(--sentra-accent-light)] cursor-pointer"
                                    onClick={() => handleDocumentToggle(source.id, doc.id)}
                                  >
                                    <div className="w-4 h-4 flex items-center justify-center">
                                      {isDocSelected && <Check size={12} className="text-green-500" />}
                                    </div>
                                    <FileText size={14} className="text-gray-400" />
                                    <span className="text-sm text-[var(--sentra-text)] truncate">
                                      {doc.display_name}
                                    </span>
                                  </div>
                                );
                              })}
                            </div>
                          )}
                        </div>
                      );
                    })
                  )}
                </div>
              )}
            </>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-2 p-4 border-t border-[var(--sentra-accent-light)]">
          <button
            onClick={handleCancel}
            className="px-4 py-2 text-[var(--sentra-text)] hover:bg-[var(--sentra-accent-light)] rounded transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleApply}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
          >
            Apply
          </button>
        </div>
      </div>
    </div>
  );
}