import { useEffect, useRef, useState } from "react";
import { ChevronDown } from "lucide-react";
import { useAppDispatch, useAppSelector } from "@store/hooks";
import { setMode } from "@features/chat/chatSlice";
import type { ConversationMode } from "@features/chat/types/mode";

const MODE_LABEL: Record<ConversationMode, string> = {
  fast: "Fast",
  plan: "Plan",
};

export default function ModeDropdown({ className = "" }: { className?: string }) {
  const dispatch = useAppDispatch();
  const mode = useAppSelector(s => s.chat.mode);
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  // Close on outside click / Escape
  useEffect(() => {
    const onClick = (e: MouseEvent) => {
      if (!ref.current?.contains(e.target as Node)) setOpen(false);
    };
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
    };
    window.addEventListener("click", onClick);
    window.addEventListener("keydown", onKey);
    return () => {
      window.removeEventListener("click", onClick);
      window.removeEventListener("keydown", onKey);
    };
  }, []);

  const select = (m: ConversationMode) => {
    dispatch(setMode(m));
    setOpen(false);
  };

  return (
    <div ref={ref} className={`relative ${className}`}>
      <span className="opacity-70">Sentra Mode: </span>
      <button
        type="button"
        onClick={() => setOpen(v => !v)}
        aria-haspopup="listbox"
        aria-expanded={open}
        className="inline-flex items-center gap-2 px-3 h-8 rounded-xl text-sm
                   bg-[var(--sentra-primary)] text-[var(--sentra-text)]
                   border border-[var(--sentra-primary)] hover:bg-[var(--sentra-primary-light)]
                   transition"
        title="Select mode"
      >
        <span className="font-medium">{MODE_LABEL[mode]}</span>
        <ChevronDown size={14} className="opacity-70" />
      </button>

      {open && (
        <div
          role="listbox"
          tabIndex={-1}
          className="absolute right-0 mt-2 min-w-[160px] rounded-xl overflow-hidden
                     border border-[var(--sentra-primary)]
                     bg-[var(--sentra-primary-dark)] shadow-xl z-50"
        >
          {(["fast","plan"] as ConversationMode[]).map(m => (
            <button
              key={m}
              role="option"
              aria-selected={mode === m}
              onClick={() => select(m)}
              className={`w-full text-left px-3 py-2 text-sm
                          hover:bg-[var(--sentra-primary)] transition
                          ${mode === m ? "bg-[var(--sentra-primary)]" : ""}`}
            >
              {MODE_LABEL[m]}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
