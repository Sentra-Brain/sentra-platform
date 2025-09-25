import { useEffect, useRef } from "react";

interface ConversationMenuProps {
  position: { top: number; left: number };
  onRename: () => void;
  onDelete: () => void;
  onRegenerate: () => void;
  onClose: () => void;
}

export function ConversationMenu({
  position,
  onRename,
  onDelete,
  onRegenerate,
  onClose,
}: ConversationMenuProps) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    // console.log("[ConversationMenu] position:", position);
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
      <button className="block w-full px-4 py-2 text-left" onClick={onRename}>
        Rename
      </button>
      <button className="block w-full px-4 py-2 text-left" onClick={onRegenerate}>
        Regenerate Title
      </button>
      <button className="block w-full px-4 py-2 text-left text-red-500" onClick={onDelete}>
        Delete
      </button>
    </div>
  );
}
