import SidebarSection from './Shared/SidebarSection'
import SidebarItem from './Shared/SidebarItem'
import { Settings, Users } from 'lucide-react'

export default function SettingsSidebar() {
  return (
    <>
      <SidebarSection title="Settings">
        <SidebarItem icon={Settings} label="System" />
        <SidebarItem icon={Users} label="Users" />
      </SidebarSection>
    </>
  )
}
