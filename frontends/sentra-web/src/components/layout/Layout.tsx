import { useState, type ReactNode } from 'react'
import { useLocation } from 'react-router-dom'
import ChatSidebar from './sidebar/ChatSidebar'
import KnowledgeSidebar from './sidebar/KnowledgeSidebar'
import SettingsSidebar from './sidebar/SettingsSidebar'
import GlobalTopBar from './GlobalTopBar'

interface Props {
  children: ReactNode
}

export default function Layout({ children }: Props) {
  const { pathname } = useLocation()
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)

  const toggleSidebar = () => setSidebarCollapsed((prev) => !prev)

  const getSidebar = () => {
    if (sidebarCollapsed) return null

    if (pathname.startsWith('/c')) return <ChatSidebar />
    if (pathname.startsWith('/k')) return <KnowledgeSidebar />
    if (pathname.startsWith('/s')) return <SettingsSidebar />
    return null
  }

  return (
    <div className="flex flex-col min-h-screen bg-sentra-primary text-sentra-text">
      {/* Always fixed at top */}
      <GlobalTopBar
        sidebarCollapsed={sidebarCollapsed}
        onToggleSidebar={toggleSidebar}
      />

      {/* Content below topbar */}
      <div className="flex flex-1 pt-14">
        {getSidebar()}
        <main className="flex-1 overflow-y-auto p-4">{children}</main>
      </div>
    </div>
  )
}
