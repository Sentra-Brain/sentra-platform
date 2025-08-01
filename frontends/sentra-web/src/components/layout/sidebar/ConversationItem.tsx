// src/components/conversations/ConversationItem.tsx

import { MoreVertical } from 'lucide-react'
import { useState } from 'react'
import clsx from 'clsx'

interface Props {
  id: string
  title: string
  active: boolean
  onSelect: (id: string) => void
  onRename: (id: string) => void
  onDelete: (id: string) => void
}

export function ConversationItem({
  id,
  title,
  active,
  onSelect,
  onRename,
  onDelete,
}: Props) {
  const [menuOpen, setMenuOpen] = useState(false)

  const handleClick = () => {
    onSelect(id)
  }

  const toggleMenu = (e: React.MouseEvent) => {
    e.stopPropagation()
    setMenuOpen((prev) => !prev)
  }

  return (
    <li
      className={clsx(
        'conversation-item',
        active ? 'active' : ''
      )}
      onClick={handleClick}
    >
      <span className="truncate text-sm">{title || 'Untitled'}</span>

      <button
        className="conversation-menu-btn"
        onClick={toggleMenu}
        title="Options"
      >
        <MoreVertical size={16} />
      </button>

      {menuOpen && (
        <div className="conversation-dropdown">
          <button
            className=""
            onClick={(e) => {
              e.stopPropagation()
              onRename(id)
              setMenuOpen(false)
            }}
          >
            Rename
          </button>
          <button
            className="danger"
            onClick={(e) => {
              e.stopPropagation()
              onDelete(id)
              setMenuOpen(false)
            }}
          >
            Delete
          </button>
        </div>
      )}
    </li>
  )
}
