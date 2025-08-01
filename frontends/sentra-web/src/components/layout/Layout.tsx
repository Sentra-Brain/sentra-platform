import type { ReactNode } from 'react'
import { useLocation } from 'react-router-dom'
import Topbar from './Topbar'
import ChatSidebar from './sidebar/ChatSidebar'
import KnowledgeSidebar from './sidebar/KnowledgeSidebar'
import SettingsSidebar from './sidebar/SettingsSidebar'

interface Props {
  children: ReactNode
}

export default function Layout({ children }: Props) {
  const { pathname } = useLocation()

  const getSidebar = () => {
    if (pathname.startsWith('/c')) return <ChatSidebar />
    if (pathname.startsWith('/k')) return <KnowledgeSidebar />
    if (pathname.startsWith('/s')) return <SettingsSidebar />
    return null
  }

  return (
    <div className="flex h-screen bg-sentra-primary text-sentra-text">
      {getSidebar()}
      <div className="flex flex-col flex-1 overflow-hidden">
        <Topbar />
        <main className="flex-1 overflow-y-auto p-4">{children}</main>
      </div>
    </div>
  )
}
