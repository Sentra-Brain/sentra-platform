import { useState, useRef, useEffect } from 'react'
import {
  Plus, Settings, Mic, Send, X, ChevronDown, Paperclip,
} from 'lucide-react'
import { useAppSelector } from '@store/hooks'
import { useChatActions } from '../hooks/useChatActions'

export default function ChatInputContainer() {
  const [value, setValue] = useState('')
  const fileInputRef = useRef<HTMLInputElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const { sendMessage } = useChatActions()
  const isStreaming = useAppSelector(s => s.chat.isStreaming)

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
    // Future: abort logic
  }

  // Auto resize
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`
    }
  }, [value])

  return (
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
  )
}
