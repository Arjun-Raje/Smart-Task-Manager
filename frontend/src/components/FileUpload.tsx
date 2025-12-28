import { useState, useRef } from "react";
import { workspaceApi } from "../api/client";
import type { TaskAttachment } from "../types";

interface Props {
  taskId: number;
  attachments: TaskAttachment[];
  onAttachmentsChange: () => void;
}

export default function FileUpload({ taskId, attachments, onAttachmentsChange }: Props) {
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      await uploadFiles(files);
    }
  };

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    if (files.length > 0) {
      await uploadFiles(files);
    }
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const uploadFiles = async (files: File[]) => {
    setUploading(true);
    setError(null);

    for (const file of files) {
      try {
        await workspaceApi.uploadAttachment(taskId, file);
      } catch (err: unknown) {
        const errorMessage = err instanceof Error ? err.message : "Upload failed";
        if (typeof err === "object" && err !== null && "response" in err) {
          const response = (err as { response?: { data?: { detail?: string } } }).response;
          setError(response?.data?.detail || errorMessage);
        } else {
          setError(errorMessage);
        }
      }
    }

    setUploading(false);
    onAttachmentsChange();
  };

  const handleDownload = async (attachment: TaskAttachment) => {
    try {
      const response = await workspaceApi.downloadAttachment(taskId, attachment.id);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", attachment.filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Download failed:", err);
    }
  };

  const handleDelete = async (attachment: TaskAttachment) => {
    if (!confirm(`Delete "${attachment.filename}"?`)) return;

    try {
      await workspaceApi.deleteAttachment(taskId, attachment.id);
      onAttachmentsChange();
    } catch (err) {
      console.error("Delete failed:", err);
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const getFileIcon = (contentType: string): string => {
    if (contentType === "application/pdf") return "📄";
    if (contentType.startsWith("image/")) return "🖼️";
    return "📎";
  };

  return (
    <div className="file-upload">
      <h3>Attachments</h3>

      <div
        className={`drop-zone ${isDragging ? "dragging" : ""} ${uploading ? "uploading" : ""}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".pdf,.png,.jpg,.jpeg,.gif,.webp"
          onChange={handleFileSelect}
          style={{ display: "none" }}
        />
        {uploading ? (
          <span>Uploading...</span>
        ) : (
          <>
            <span className="drop-icon">📁</span>
            <span>Drop files here or click to upload</span>
            <span className="file-types">PDF, PNG, JPG, GIF, WEBP (max 10MB)</span>
          </>
        )}
      </div>

      {error && <div className="upload-error">{error}</div>}

      {attachments.length > 0 && (
        <ul className="attachments-list">
          {attachments.map((attachment) => (
            <li key={attachment.id} className="attachment-item">
              <span className="attachment-icon">{getFileIcon(attachment.content_type)}</span>
              <div className="attachment-info">
                <span className="attachment-name">{attachment.filename}</span>
                <span className="attachment-size">{formatFileSize(attachment.file_size)}</span>
              </div>
              <div className="attachment-actions">
                <button
                  className="action-btn download"
                  onClick={() => handleDownload(attachment)}
                  title="Download"
                >
                  ⬇️
                </button>
                <button
                  className="action-btn delete"
                  onClick={() => handleDelete(attachment)}
                  title="Delete"
                >
                  🗑️
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}

      {attachments.length === 0 && (
        <p className="no-attachments">No attachments yet</p>
      )}
    </div>
  );
}
