// src/components/conversations/ConversationItem.tsx

import { MoreVertical } from "lucide-react";
import { useState } from "react";
import clsx from "clsx";

interface Props {
  id: string;
  title: string;
  active: boolean;
  onSelect: (id: string) => void;
  onRename: (id: string) => void;
  onDelete: (id: string) => void;
}

export function ConversationItem({
  id,
  title,
  active,
  onSelect,
  onRename,
  onDelete,
}: Props) {
  const [menuOpen, setMenuOpen] = useState(false);

  const handleClick = () => {
    onSelect(id);
  };

  const toggleMenu = (e: React.MouseEvent) => {
    e.stopPropagation();
    setMenuOpen((prev) => !prev);
  };

  return (
    <li
      className={clsx(
        "relative flex items-center justify-between px-3 py-2 rounded-md text-sm font-medium transition-colors cursor-pointer group",
        active
          ? "bg-[var(--sentra-accent)] text-[var(--sentra-primary)]"
          : "hover:bg-[var(--sentra-primary-light)] text-[var(--sentra-text)]"
      )}
      onClick={handleClick}
    >
      {/* Título de la conversación */}
      <span className="truncate flex-1">{title || "Untitled"}</span>

      {/* Botón de opciones */}
      <button
        onClick={toggleMenu}
        title="Options"
        className="ml-2 p-1 rounded hover:bg-[var(--sentra-primary-light)] transition"
        onClickCapture={(e) => e.stopPropagation()}
      >
        <MoreVertical size={16} />
      </button>

      {/* Menú contextual */}
      {menuOpen && (
        <div
          className="
        absolute top-full right-2 mt-1 w-28 z-50
        bg-[var(--sentra-primary-dark)]
        border border-[var(--sentra-accent-light)]
        rounded-md shadow-lg py-1
      "
          onClick={(e) => e.stopPropagation()}
        >
          <button
            className="w-full px-3 py-1 text-left text-sm hover:bg-[var(--sentra-accent-light)]"
            onClick={() => {
              onRename(id);
              setMenuOpen(false);
            }}
          >
            Rename
          </button>
          <button
            className="w-full px-3 py-1 text-left text-sm text-red-500 hover:bg-red-100 hover:text-red-700"
            onClick={() => {
              onDelete(id);
              setMenuOpen(false);
            }}
          >
            Delete
          </button>
        </div>
      )}
    </li>
  );
}
