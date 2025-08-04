// src/layout/GlobalMenuPanel.tsx

import { X } from 'lucide-react'
import { useEffect } from 'react'

interface Props {
  open: boolean
  onClose: () => void
}

export default function GlobalMenuPanel({ open, onClose }: Props) {
  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    document.addEventListener('keydown', handleKey)
    return () => document.removeEventListener('keydown', handleKey)
  }, [onClose])

  return (
    <>
      {/* Overlay */}
      {open && (
        <div
          onClick={onClose}
          className="fixed inset-0 bg-black bg-opacity-40 z-40 transition-opacity"
        />
      )}

      {/* Panel */}
      <div
        className={`
          fixed top-0 left-0 h-full w-[280px] z-50 
          bg-[var(--sentra-primary-dark)] border-r border-[var(--sentra-primary)]
          shadow-lg transform transition-transform
          ${open ? 'translate-x-0' : '-translate-x-full'}
        `}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-[var(--sentra-primary)]">
          <span className="text-[var(--sentra-text)] font-semibold">Menu</span>
          <button
            onClick={onClose}
            className="p-1 text-[var(--sentra-text)] hover:bg-[var(--sentra-primary)] rounded"
          >
            <X size={20} />
          </button>
        </div>

        {/* Links or content */}
        <nav className="flex flex-col p-4 text-sm text-[var(--sentra-text)] gap-3">
          <a href="/" className="hover:text-[var(--sentra-accent)]">🏠 Home</a>
          <a href="/c" className="hover:text-[var(--sentra-accent)]">💬 Chat</a>
          <a href="/k" className="hover:text-[var(--sentra-accent)]">📚 Knowledge</a>
          <a href="/settings" className="hover:text-[var(--sentra-accent)]">⚙️ Settings</a>
          <a href="https://github.com/jgccon/sentra-brain" target="_blank" className="hover:text-[var(--sentra-accent)]">🌐 GitHub</a>
        </nav>
      </div>
    </>
  )
}
