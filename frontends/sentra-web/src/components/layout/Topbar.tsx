import { useDispatch, useSelector } from 'react-redux'
import type { RootState } from '../../store'
import { toggleSidebar } from '../../store/slices/uiSlice'
import UserMenu from './UserMenu'

export default function Topbar() {
  const dispatch = useDispatch()
  const isCollapsed = useSelector((state: RootState) => state.ui.isSidebarCollapsed)

  return (
    <header className="h-14 flex items-center justify-between px-4 border-b border-gray-700 bg-sentra-primary-dark">
      <div className="flex items-center gap-4">
        <button onClick={() => dispatch(toggleSidebar())}>
          <svg
            className="w-6 h-6"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
        {isCollapsed && <div className="sidebar-collapsed">Sidebar is collapsed</div>}
        <input
          type="text"
          placeholder="Search..."
          className="bg-sentra-primary rounded px-3 py-1 text-sm w-64 outline-none border border-gray-600 focus:ring-1 focus:ring-sentra-accent"
        />
      </div>

      <UserMenu />
    </header>
  )
}
