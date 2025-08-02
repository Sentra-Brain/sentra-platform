import { useEffect, useRef } from "react";

interface ConversationMenuProps {
  position: { top: number; left: number };
  onRename: () => void;
  onDelete: () => void;
  onClose: () => void;
}

export function ConversationMenu({
  position,
  onRename,
  onDelete,
  onClose,
}: ConversationMenuProps) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    console.log("[ConversationMenu] position:", position);
  }, [position]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (ref.current && !ref.current.contains(event.target as Node)) {
        onClose();
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [onClose]);

  return (
    <div
      ref={ref}
      className="fixed z-50 w-40 rounded-md border border-[var(--sentra-accent-light)] bg-[var(--sentra-primary-dark)] shadow-lg py-1"
      style={{
        top: `${position.top}px`,
        left: `${position.left}px`,
      }}
    >
      <button
        className="w-full px-3 py-1 text-left text-sm hover:bg-[var(--sentra-accent-light)]"
        onClick={onRename}
      >
        Rename
      </button>
      <button
        className="w-full px-3 py-1 text-left text-sm text-red-500 hover:bg-red-100 hover:text-red-700"
        onClick={onDelete}
      >
        Delete
      </button>
    </div>
  );
}
