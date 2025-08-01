import type { LucideIcon } from 'lucide-react'

interface SidebarItemProps {
  icon: LucideIcon
  label: string
  onClick?: () => void
  active?: boolean
}

export default function SidebarItem({ icon: Icon, label, onClick, active }: SidebarItemProps) {
  return (
    <button
      onClick={onClick}
      className={`group flex items-center w-full px-3 py-2 text-sm font-medium rounded-md transition-colors
        ${active ? 'bg-sentra-accent text-white' : 'hover:bg-sentra-accent-light text-gray-300'}`}
    >
      <Icon className="w-4 h-4 mr-2" />
      {label}
    </button>
  )
}
