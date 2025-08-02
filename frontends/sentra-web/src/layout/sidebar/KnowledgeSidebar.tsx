import SidebarSection from './Shared/SidebarSection'
import SidebarItem from './Shared/SidebarItem'
import { Book } from 'lucide-react'

export default function KnowledgeSidebar() {
  return (
    <>
      <SidebarSection title="Sources">
        <SidebarItem icon={Book} label="My sources" />
        {/* TODO: Render list of knowledge sources */}
      </SidebarSection>
    </>
  )
}
