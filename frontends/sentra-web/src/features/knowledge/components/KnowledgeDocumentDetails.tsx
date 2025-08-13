import { useEffect, useState } from "react";
import {
  RefreshCw,
  Save,
  Eye,
  EyeOff,
} from "lucide-react";
import type { KnowledgeDocument } from "../types/knowledgeModels";
import { useKnowledge } from "../useKnowledge";
import DocumentStatusBadge from "./DocumentStatusBadge";
import MarkdownPreviewPanel from "./MarkdownPreviewPanel";

interface Props {
  document: KnowledgeDocument;
}

export default function KnowledgeDocumentDetails({ document }: Props) {
  const {
    updateDocumentMetadata,
    reindexDocument,
    fetchMarkdown,
    markdownByDocId,
    loadingMarkdownFor,
  } = useKnowledge();

  const [displayName, setDisplayName] = useState(document.display_name);
  const [description, setDescription] = useState(document.description ?? "");
  const [saving, setSaving] = useState(false);
  const [showMarkdown, setShowMarkdown] = useState(false);

  useEffect(() => {
    // Reset panel when switching docs
    setDisplayName(document.display_name);
    setDescription(document.description ?? "");
    setShowMarkdown(false);
  }, [document.id]);

  const handleSave = async () => {
    setSaving(true);
    try {
      await updateDocumentMetadata(document.id, {
        display_name: displayName.trim(),
        description: description.trim(),
      });
    } catch (err) {
      console.error("Failed to save document metadata:", err);
      alert("Failed to save");
    } finally {
      setSaving(false);
    }
  };

  const toggleMarkdown = async () => {
    if (!markdownByDocId[document.id]) {
      await fetchMarkdown(document.id);
    }
    setShowMarkdown((prev) => !prev);
  };

  return (
    <div className="space-y-6 text-sm relative">
      {/* Title + status */}
      <div className="flex items-start justify-between">
        <div>
          <h2 className="text-xl font-semibold flex items-center gap-2">
            📄 {displayName || "(Untitled)"}
          </h2>
          <div className="text-xs text-muted italic truncate max-w-md">
            {document.filename}
          </div>
        </div>

        <div className="flex flex-col items-end">
          <DocumentStatusBadge status={document.status} />
        </div>
      </div>

      {/* Editable fields */}
      <div className="grid grid-cols-1 gap-4">
        <div>
          <label className="text-xs uppercase text-muted font-medium mb-1 block">
            Display Name
          </label>
          <input
            value={displayName}
            onChange={(e) => setDisplayName(e.target.value)}
            className="w-full px-3 py-2 rounded bg-[var(--sentra-primary-dark)]"
          />
        </div>

        <div>
          <label className="text-xs uppercase text-muted font-medium mb-1 block">
            Description
          </label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full px-3 py-2 rounded bg-[var(--sentra-primary-dark)]"
            rows={3}
          />
        </div>
      </div>

      {/* Status messages */}
      {document.status_message && (
        <div className="text-xs text-muted italic">{document.status_message}</div>
      )}
      {document.error && (
        <div className="text-xs text-red-400">❌ {document.error}</div>
      )}

      {/* Footer actions */}
      <div className="flex justify-between items-center mt-4">
        <div className="text-xs text-muted">
          Created by {document.created_by.full_name} on{" "}
          {new Date(document.created_at).toLocaleString()}
        </div>
        <div className="flex gap-2">


          {document.has_markdown && (
            <button
              className="btn border border-green-500 mt-2 text-xs flex items-center gap-1"
              onClick={toggleMarkdown}
              disabled={loadingMarkdownFor === document.id}
            >
              {showMarkdown ? (
                <EyeOff className="w-4 h-4" />
              ) : (
                <Eye className="w-4 h-4" />
              )}
              {loadingMarkdownFor === document.id
                ? "Loading..."
                : showMarkdown
                ? "Hide Markdown"
                : "View Markdown"}
            </button>
          )}
          <button
            onClick={() => reindexDocument(document.id)}
              className="btn border border-orange-500 mt-2 text-xs flex items-center gap-1"
          >
            <RefreshCw className="w-4 h-4" /> Reindex
          </button>
          <button
            onClick={handleSave}
              className="btn btn-primary mt-2 text-xs flex items-center gap-1"
            disabled={saving}
          >
            <Save className="w-4 h-4" />{" "}
            {saving ? "Saving..." : "Save Changes"}
          </button>
        </div>
      </div>

      {/* Markdown floating panel */}
      {showMarkdown && markdownByDocId[document.id] && (
        <MarkdownPreviewPanel
          markdown={markdownByDocId[document.id]}
          onClose={() => setShowMarkdown(false)}
        />
      )}
    </div>
  );
}
