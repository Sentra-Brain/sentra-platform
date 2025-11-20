import type { ReactNode } from 'react'

export default function ChatFooter({ children }: { children: ReactNode }) {
  return (
    <div className="px-4 py-3 border-t border-[var(--sentra-accent-light)]">
      <div className="w-full max-w-[768px] mx-auto">
        {children}
      </div>
    </div>
  )
}
