import type { ReactNode } from 'react'

interface SidebarGroupProps {
  children: ReactNode
}

export default function SidebarGroup({ children }: SidebarGroupProps) {
  return (
    <div className="mb-4">
      {children}
    </div>
  )
}
