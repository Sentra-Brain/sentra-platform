import type { ReactNode } from 'react'

interface SidebarSectionProps {
  title: string
  children: ReactNode
}

export default function SidebarSection({ title, children }: SidebarSectionProps) {
  return (
    <div className="mb-4">
      <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-wider px-3 mb-2">
        {title}
      </h2>
      <div className="space-y-1 px-2">
        {children}
      </div>
    </div>
  )
}
