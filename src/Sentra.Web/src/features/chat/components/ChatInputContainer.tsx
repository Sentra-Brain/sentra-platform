import { useState, useRef, useEffect } from 'react'
import {
  Plus, Settings, Mic, Send, X, ChevronDown, Paperclip, BookOpen,
} from 'lucide-react'
import { useAppSelector, useAppDispatch } from '@store/hooks'
import { useChatActions } from '../hooks/useChatActions'
import { 
  removeContextSource, 
  removeContextDocument, 
  clearSelectedContext 
} from '../eventsSlice'
import ContextSelectorPanel from './ContextSelectorPanel'
import ContextChip from './ContextChip'

export default function ChatInputContainer() {
  const [value, setValue] = useState('')
  const [showContextSelector, setShowContextSelector] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const dispatch = useAppDispatch()
  const { sendMessage, stopStreaming } = useChatActions()
  const isStreaming = useAppSelector(s => s.events.isStreaming)
  const { selectedContext } = useAppSelector(s => s.events)
  const sources = useAppSelector(s => s.knowledge.sources)
  const documentsBySource = useAppSelector(s => s.knowledge.documentsBySource)

  const handleSend = async () => {
    await sendMessage(value)
    setValue('')
  }

  const handleKeyDown = async (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      await handleSend()
    }
  }

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.target.value = ''
  }

  const handleStop = () => {
    stopStreaming()
  }

  const handleContextSelectorOpen = () => {
    setShowContextSelector(true)
  }

  const handleContextSelectorClose = () => {
    setShowContextSelector(false)
  }

  const handleContextApply = () => {
    setShowContextSelector(false)
  }

  const handleRemoveSource = (sourceId: string) => {
    dispatch(removeContextSource(sourceId))
  }

  const handleRemoveDocument = (documentId: string) => {
    dispatch(removeContextDocument(documentId))
  }

  const handleClearAllContext = () => {
    dispatch(clearSelectedContext())
  }

  // Get display names for context chips
  const getSourceName = (sourceId: string) => {
    const source = sources.find(s => s.id === sourceId)
    return source?.name || 'Unknown Source'
  }

  const getDocumentName = (documentId: string) => {
    for (const docs of Object.values(documentsBySource)) {
      const doc = docs.find(d => d.id === documentId)
      if (doc) return doc.display_name
    }
    return 'Unknown Document'
  }

  const hasSelectedContext = selectedContext.useRag && 
    (selectedContext.sourceIds.length > 0 || selectedContext.documentIds.length > 0)

  // Auto resize
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`
    }
  }, [value])

  return (
    <>
      <div className="
        w-full max-w-[768px]
        border border-[var(--sentra-accent-light)]
        bg-[var(--sentra-primary-dark)]
        rounded-xl shadow-md
        px-4 py-3
        flex flex-col gap-2
        focus-within:ring-2 focus-within:ring-blue-500
        transition-all duration-200
      ">
        {/* Context chips display */}
        {hasSelectedContext && (
          <div className="flex flex-wrap items-center gap-2 pb-2 border-b border-[var(--sentra-accent-light)]">
            <span className="text-sm text-[var(--sentra-muted)]">Context:</span>
            
            {/* Source chips */}
            {selectedContext.sourceIds.map(sourceId => (
              <ContextChip
                key={`source-${sourceId}`}
                type="source"
                name={getSourceName(sourceId)}
                onRemove={() => handleRemoveSource(sourceId)}
                onEdit={handleContextSelectorOpen}
              />
            ))}
            
            {/* Document chips */}
            {selectedContext.documentIds.map(documentId => (
              <ContextChip
                key={`doc-${documentId}`}
                type="document"
                name={getDocumentName(documentId)}
                onRemove={() => handleRemoveDocument(documentId)}
                onEdit={handleContextSelectorOpen}
              />
            ))}
            
            {/* Clear all button */}
            <button
              onClick={handleClearAllContext}
              className="text-xs text-red-500 hover:text-red-400 underline ml-2"
              title="Clear all context"
            >
              Clear all
            </button>
          </div>
        )}

        {/* Text input */}
        <div className="w-full">
          <textarea
            ref={textareaRef}
            className="
              w-full max-h-[200px] min-h-[32px]
              resize-none overflow-y-auto
              bg-transparent
              text-[var(--sentra-text)] placeholder-[var(--sentra-muted)]
              focus:outline-none
              scrollbar-thin scrollbar-thumb-[var(--sentra-accent-light)]
              pr-1
            "
            rows={1}
            placeholder="Type a message..."
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isStreaming}
          />
        </div>

        {/* Toolbar */}
        <div className="flex items-center justify-between gap-2 flex-wrap">
          <div className="flex items-center gap-2">
            <button className="icon-btn" disabled title="Coming soon">
              <Plus size={18} />
            </button>
            <button className="icon-btn" disabled title="Coming soon">
              <Paperclip size={18} />
            </button>
            <button 
              className={`icon-btn ${hasSelectedContext ? 'active' : ''}`}
              onClick={handleContextSelectorOpen}
              title="Select context sources"
            >
              <BookOpen size={18} />
            </button>
            <button className="icon-btn" disabled title="Tools (coming soon)">
              <Settings size={18} />
            </button>
          </div>

          <input type="file" ref={fileInputRef} hidden onChange={handleFileUpload} />

          <div className="flex items-center gap-2">
            <button className="icon-btn" disabled title="Dictate (coming soon)">
              <Mic size={18} />
            </button>

            {isStreaming ? (
              <button className="icon-btn" onClick={handleStop} title="Stop">
                <X size={18} />
              </button>
            ) : (
              <button
                className="icon-btn send"
                onClick={handleSend}
                title="Send"
                disabled={!value.trim()}
              >
                <Send size={18} />
              </button>
            )}

            <button className="icon-btn" title="Scroll to bottom">
              <ChevronDown size={20} />
            </button>
          </div>
        </div>
      </div>

      {/* Context Selector Panel */}
      <ContextSelectorPanel
        isOpen={showContextSelector}
        onClose={handleContextSelectorClose}
        onApply={handleContextApply}
      />
    </>
  )
}
