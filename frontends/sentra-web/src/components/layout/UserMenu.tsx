export default function UserMenu() {
  return (
    <div className="flex items-center gap-2">
      <span className="text-sm hidden md:inline">John Doe</span>
      <img
        src="/avatar.png"
        alt="avatar"
        className="w-8 h-8 rounded-full border border-gray-400"
      />
    </div>
  )
}
