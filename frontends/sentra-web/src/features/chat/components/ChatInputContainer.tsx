import { useState, useRef } from 'react'
import {
  Plus, Settings, Mic, Send, X, ChevronDown, Paperclip,
} from 'lucide-react'
import { useAppSelector } from '@store/hooks'
import { useChatActions } from '../hooks/useChatActions'

export default function ChatInputContainer() {
  const [value, setValue] = useState('')
  const fileInputRef = useRef<HTMLInputElement>(null)

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
    // Future: handle abort logic
  }

  return (
    <div className="w-full max-w-[768px] bg-[var(--sentra-primary-dark)] border border-[var(--sentra-accent-light)] rounded-xl px-4 py-3 shadow-md flex items-end gap-2">
      <button className="icon-btn" disabled title="Coming soon">
        <Plus size={18} />
      </button>
      <button className="icon-btn" disabled title="Coming soon">
        <Paperclip size={18} />
      </button>
      <button className="icon-btn" disabled title="Tools (coming soon)">
        <Settings size={18} />
      </button>

      <div className="flex-1">
        <textarea
          className="w-full resize-none bg-transparent text-[var(--sentra-text)] placeholder-[var(--sentra-muted)] focus:outline-none"
          rows={1}
          placeholder="Type a message..."
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isStreaming}
        />
      </div>

      <input type="file" ref={fileInputRef} hidden onChange={handleFileUpload} />

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
  )
}
