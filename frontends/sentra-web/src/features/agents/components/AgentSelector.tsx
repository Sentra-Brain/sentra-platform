import { useEffect, useRef, useState } from "react";
import { ChevronDown, Bot } from "lucide-react";
import { useAppDispatch, useAppSelector } from "@store/hooks";
import { fetchAgents, selectAgent } from "../agentsSlice";

export default function AgentSelector({ className = "" }: { className?: string }) {
  const dispatch = useAppDispatch();
  const { agents, loading, error, selected } = useAppSelector((s) => s.agents);
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  // Load agents on mount
  useEffect(() => {
    if (!agents.length && !loading) dispatch(fetchAgents());
  }, [agents.length, loading, dispatch]);

  // Close dropdown on outside click / Esc
  useEffect(() => {
    const onClick = (e: MouseEvent) => {
      if (!ref.current?.contains(e.target as Node)) setOpen(false);
    };
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && setOpen(false);
    window.addEventListener("click", onClick);
    window.addEventListener("keydown", onKey);
    return () => {
      window.removeEventListener("click", onClick);
      window.removeEventListener("keydown", onKey);
    };
  }, []);

  const handleSelect = (key: string) => {
    const agent = agents.find((a) => a.key === key) || null;
    dispatch(selectAgent(agent));
    setOpen(false);
  };

  if (loading && !agents.length)
    return <div className="text-sm opacity-70">Loading agents…</div>;
  if (error)
    return <div className="text-sm text-red-500">Failed to load agents</div>;

  return (
    <div ref={ref} className={`relative ${className}`}>
      <span className="opacity-70 text-sm"> Agents ({agents.length}): </span>

      {/* Main button */}
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-haspopup="listbox"
        aria-expanded={open}
        className="inline-flex items-center gap-2 px-3 h-8 rounded-xl text-sm
                   bg-[var(--sentra-primary)] text-[var(--sentra-text)]
                   border border-[var(--sentra-primary)]
                   hover:bg-[var(--sentra-primary-light)] transition"
        title="Select agent"
      >
        {/* Geek / bot icon */}
        <Bot className="h-4 w-4 flex-shrink-0" />

        <span className="font-medium truncate max-w-[120px]">
          {selected?.name || "Select Agent"}
        </span>
        <ChevronDown size={14} className="opacity-70" />
      </button>

      {/* Dropdown */}
      {open && (
        <div
          role="listbox"
          tabIndex={-1}
          className="absolute right-0 mt-2 min-w-[180px] rounded-xl overflow-hidden
                     border border-[var(--sentra-primary)]
                     bg-[var(--sentra-primary-dark)] shadow-xl z-50"
        >
          {agents.map((a) => (
            <button
              key={a.key}
              role="option"
              aria-selected={selected?.key === a.key}
              onClick={() => handleSelect(a.key)}
              className={`w-full text-left px-3 py-2 text-sm flex items-center gap-2
                          hover:bg-[var(--sentra-primary)] transition
                          ${selected?.key === a.key ? "bg-[var(--sentra-primary)]" : ""}`}
            >
              <Bot className="h-4 w-4 flex-shrink-0 text-[var(--sentra-accent)]" />
              <span className="truncate">{a.name || a.key}</span>
            </button>
          ))}

          {agents.length === 0 && (
            <div className="px-3 py-2 text-sm text-gray-400">
              No agents found
            </div>
          )}
        </div>
      )}
    </div>
  );
}
