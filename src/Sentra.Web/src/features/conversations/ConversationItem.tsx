import { MoreHorizontal } from "lucide-react";
import { useRef, useState, type MouseEvent } from "react";
import clsx from "clsx";
import { ConversationMenu } from "./ConversationMenu"

interface Props {
  id: string;
  title: string;
  active: boolean;
  onSelect: (id: string) => void;
  onRename: (id: string) => void;
  onDelete: (id: string) => void;
  onRegenerate: (id: string) => void;
}

export function ConversationItem({
  id,
  title,
  active,
  onSelect,
  onRename,
  onDelete,
  onRegenerate,
}: Props) {
  const buttonRef = useRef<HTMLButtonElement>(null);
  const [menuOpen, setMenuOpen] = useState(false);
  const [menuPosition, setMenuPosition] = useState({ top: 0, left: 0 });

  const handleClick = () => {
    onSelect(id);
  };

  const toggleMenu = (e: MouseEvent<HTMLButtonElement>) => {
    e.stopPropagation();
    if (buttonRef.current) {
      const rect = buttonRef.current.getBoundingClientRect();
      setMenuPosition({
        top: rect.bottom + window.scrollY,
        left: rect.left + window.scrollX,
      });
    }
    setMenuOpen((open) => !open);
  };

  return (
    <div
      className={clsx(
        "flex items-center justify-between px-2 py-1 cursor-pointer",
        active && "bg-[var(--sentra-accent-light)]"
      )}
      onClick={handleClick}
    >
      <span className="truncate flex-1">{title}</span>
      <button
        ref={buttonRef}
        className="ml-2 p-1 rounded hover:bg-[var(--sentra-accent-light)]"
        onClick={toggleMenu}
      >
        <MoreHorizontal size={16} />
      </button>
      {menuOpen && (
        <ConversationMenu
          position={menuPosition}
          onRename={() => onRename(id)}
          onDelete={() => onDelete(id)}
          onRegenerate={() => onRegenerate(id)}
          onClose={() => setMenuOpen(false)}
        />
      )}
    </div>
  );
}
