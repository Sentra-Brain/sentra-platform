// features/knowledge/components/MarkdownPreviewPanel.tsx
import { X } from "lucide-react";
import { useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";

interface Props {
  markdown: string;
  onClose: () => void;
}

export default function MarkdownPreviewPanel({ markdown, onClose }: Props) {
  const panelRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleOutsideClick = (e: MouseEvent) => {
      if (panelRef.current && !panelRef.current.contains(e.target as Node)) {
        onClose();
      }
    };
    document.addEventListener("mousedown", handleOutsideClick);
    return () => document.removeEventListener("mousedown", handleOutsideClick);
  }, [onClose]);

  return (
    <div className="fixed inset-0 z-50 flex justify-end items-start">
      {/* Overlay for click outside */}
      <div className="absolute inset-0 bg-black/30 backdrop-blur-sm" />

      {/* Side panel */}
      <div
        ref={panelRef}
        className="relative w-[50vw] max-w-[750px] h-full bg-[--sentra-primary] text-sm border-l border-[--sentra-accent] shadow-xl z-50 flex flex-col"
      >
        {/* Header */}
<div className="flex justify-between items-center px-4 py-3 border-b border-[--sentra-accent] bg-[--sentra-primary-dark]">
  <div className="text-sm font-medium text-muted">Markdown Preview</div>
  <button
    className="text-red-400 hover:text-red-200 transition"
    onClick={onClose}
  >
    <X className="w-5 h-5" />
  </button>
</div>

{/* Content */}
<div className="p-4 overflow-y-auto prose dark:prose-invert max-w-none text-[--sentra-text]">
  <div className="bg-red-900/30 border border-red-700 text-red-300 text-xs italic rounded px-3 py-2 mb-4">
    ⚠️ This is an automated Markdown extraction. Some content like tables,
    images, or complex formatting might not appear correctly.
  </div>
  <ReactMarkdown>{markdown}</ReactMarkdown>
</div>

      </div>
    </div>
  );
}
