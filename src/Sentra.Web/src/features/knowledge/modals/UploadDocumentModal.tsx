// features/knowledge/modals/UploadDocumentModal.tsx
import { useEffect, useState } from "react";
import { X, Upload, File } from "lucide-react";
import { useKnowledge } from "../useKnowledge";

interface Props {
  isOpen: boolean;
  onClose: () => void;
}

export default function UploadDocumentModal({ isOpen, onClose }: Props) {
  const {
    visibility,
    sources,
    selectedSourceId,
    uploadToSource,
    loadDocuments,
  } = useKnowledge();

  const visibleSources = sources.filter((s) => s.visibility === visibility);

  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [targetSourceId, setTargetSourceId] = useState<string | undefined>(
    selectedSourceId ?? visibleSources[0]?.id
  );
  const [uploading, setUploading] = useState(false);

  // Asegura que cuando se abre el modal, se use el source seleccionado o el primero visible
  useEffect(() => {
    if (
      !targetSourceId &&
      isOpen &&
      (selectedSourceId || visibleSources.length > 0)
    ) {
      setTargetSourceId(selectedSourceId ?? visibleSources[0]?.id);
    }
  }, [isOpen, selectedSourceId, visibleSources, targetSourceId]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setSelectedFiles(Array.from(e.target.files));
    }
  };

  const handleUpload = async () => {
    if (!targetSourceId || selectedFiles.length === 0) return;

    setUploading(true);
    try {
      for (const file of selectedFiles) {
        const displayName = file.name.replace(/\.[^/.]+$/, "");
        await uploadToSource(targetSourceId, file, {
          display_name: displayName,
        });
      }
      loadDocuments(targetSourceId, true);
      onClose();
    } catch (error) {
      console.error(error);
      alert("Upload failed");
    } finally {
      setUploading(false);
    }
  };

  const handleCancel = () => {
    if (!uploading) {
      setSelectedFiles([]);
      setTargetSourceId(selectedSourceId ?? visibleSources[0]?.id);
      onClose();
    }
  };

  const formatSize = (bytes: number) => {
    const sizes = ["Bytes", "KB", "MB"];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`;
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black bg-opacity-50 flex items-center justify-center">
      <div className="bg-[var(--sentra-primary-dark)] w-full max-w-lg rounded-lg p-6 border border-[var(--sentra-accent-light)] relative">
        <button
          onClick={handleCancel}
          className="absolute top-3 right-3 text-[var(--sentra-text-muted)] hover:text-white"
          disabled={uploading}
        >
          <X className="w-5 h-5" />
        </button>

        <h2 className="text-lg font-semibold mb-4">📤 Upload Documents</h2>

        <div className="space-y-4">
          {/* Source dropdown */}
          <select
            value={targetSourceId}
            onChange={(e) => setTargetSourceId(e.target.value)}
            className="w-full px-3 py-2 rounded bg-[var(--sentra-primary)]"
            disabled={uploading}
          >
            {visibleSources.map((s) => (
              <option key={s.id} value={s.id}>
                {s.name}
              </option>
            ))}
          </select>

          {/* File input */}
          <label className="flex flex-col items-center gap-2 px-4 py-6 bg-[var(--sentra-primary)] rounded border-2 border-dashed cursor-pointer text-sm">
            <Upload className="w-6 h-6" />
            <span>Click to select files or drag and drop</span>
            <small className="text-xs text-muted">
              Supported: PDF, DOCX, TXT, MD
            </small>
            <input
              type="file"
              multiple
              accept=".pdf,.docx,.txt,.md"
              className="hidden"
              onChange={handleFileChange}
              disabled={uploading}
            />
          </label>

          {/* Selected files */}
          {selectedFiles.length > 0 && (
            <div className="bg-[var(--sentra-primary)] rounded p-2 text-sm max-h-40 overflow-y-auto">
              {selectedFiles.map((file, idx) => (
                <div key={idx} className="flex items-center gap-2">
                  <File className="w-4 h-4" />
                  <span className="flex-1 truncate">{file.name}</span>
                  <span className="text-xs text-muted">
                    {formatSize(file.size)}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="flex justify-end mt-4 gap-2">
          <button
            onClick={handleCancel}
            className="btn btn-secondary"
            disabled={uploading}
          >
            Cancel
          </button>
          <button
            onClick={handleUpload}
            className="btn btn-primary"
            disabled={
              uploading || selectedFiles.length === 0 || !targetSourceId
            }
          >
            {uploading
              ? "Uploading..."
              : `Upload ${selectedFiles.length} file(s)`}
          </button>
        </div>
      </div>
    </div>
  );
}
