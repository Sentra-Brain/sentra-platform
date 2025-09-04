import { MoreHorizontal } from "lucide-react";
import { useRef, useState, type MouseEvent } from "react";
import clsx from "clsx";
import { SessionMenu } from "./SessionMenu";

interface Props {
  id: string;
  title: string;
  active: boolean;
  onSelect: (id: string) => void;
  onRename: (id: string) => void;
  onDelete: (id: string) => void;
}

export function SessionItem({
  id,
  title,
  active,
  onSelect,
  onRename,
  onDelete,
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
      setMenuOpen((prev) => !prev);
    }
  };

  return (
    <li
      className={clsx(
        "relative flex items-center justify-between px-3 rounded-md text-sm font-medium transition-colors cursor-pointer group",
        active
          ? "bg-[var(--sentra-accent)] text-[var(--sentra-primary)]"
          : "hover:bg-[var(--sentra-primary-light)] text-[var(--sentra-text)]"
      )}
      onClick={handleClick}
    >
      <span className="truncate flex-1">{title || "Untitled"}</span>

      <button
        ref={buttonRef}
        onClick={toggleMenu}
        title="Options"
        className="
          invisible group-hover:visible
          p-0 m-0
          text-[var(--sentra-text)]
          hover:text-[var(--sentra-accent-light)]
          transition
        "
      >
        <MoreHorizontal size={16} />
      </button>

      {menuOpen && (
        <SessionMenu
          position={menuPosition}
          onRename={() => {
            onRename(id);
            setMenuOpen(false);
          }}
          onDelete={() => {
            onDelete(id);
            setMenuOpen(false);
          }}
          onClose={() => setMenuOpen(false)}
        />
      )}
    </li>
  );
}
