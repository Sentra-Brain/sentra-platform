// features/knowledge/KnowledgePage.tsx
import { useParams, useNavigate } from "react-router-dom";
import { useEffect } from "react";
import { useKnowledge } from "./useKnowledge";
import KnowledgeSourceList from "./components/KnowledgeSourceList";
import KnowledgeDetailsPanel from "./components/KnowledgeDetailsPanel";
import type { KnowledgeSourceVisibility } from "./types/knowledgeModels";
import KnowledgeToolbar from "./components/KnowledgeToolbar";

export default function KnowledgePage() {
  const navigate = useNavigate();
  const {
    visibility: visibilityParam,
    sourceId,
    documentId,
  } = useParams<{
    visibility: string;
    sourceId?: string;
    documentId?: string;
  }>();

  const {
    visibility,
    sources,
    changeVisibility,
    loadSources,
    loadDocuments,
    selectSourceById,
    selectDocumentById,
    selectedSourceId,
  } = useKnowledge();

  // Ensure the URL param maps to a valid visibility
  useEffect(() => {
    const allowed: KnowledgeSourceVisibility[] = [
      "private",
      "shared",
      "org-wide",
    ];
    const param = visibilityParam as KnowledgeSourceVisibility;

    if (!param || !allowed.includes(param)) {
      navigate("/k/private", { replace: true });
    } else if (param !== visibility) {
      changeVisibility(param);
    }
  }, [visibilityParam, visibility, navigate, changeVisibility]);

  useEffect(() => {
    const allowed: KnowledgeSourceVisibility[] = [
      "private",
      "shared",
      "org-wide",
    ];
    const param = visibilityParam as KnowledgeSourceVisibility;

    if (!param || !allowed.includes(param)) {
      navigate("/k/private", { replace: true });
    } else if (param !== visibility) {
      changeVisibility(param);
    }
  }, [visibilityParam, visibility, navigate, changeVisibility]);

  useEffect(() => {
    if (sources.length === 0) {
      loadSources();
    }
  }, [sources.length, loadSources]);

  useEffect(() => {
    if (sourceId) selectSourceById(sourceId);
    if (documentId) selectDocumentById(documentId);
  }, [sourceId, documentId]);

  useEffect(() => {
    if (selectedSourceId) loadDocuments(selectedSourceId);
  }, [selectedSourceId, loadDocuments]);

  return (
    <div className="p-4 h-full flex flex-col gap-4">
      <h1 className="text-xl font-semibold">📚 Knowledge Management</h1>

      <KnowledgeToolbar visibility={visibility} />

      <div className="flex flex-1 overflow-hidden">
        <div className="w-1/3 overflow-y-auto pr-4">
          <KnowledgeSourceList visibility={visibility} />
        </div>
        <div className="flex-1 overflow-y-auto pl-4 border-l border-[var(--sentra-primary-light)]">
          <KnowledgeDetailsPanel />
        </div>
      </div>
    </div>
  );
}
