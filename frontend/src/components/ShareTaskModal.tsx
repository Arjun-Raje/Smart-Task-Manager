import { useState, useEffect } from "react";
import { shareApi } from "../api/client";
import type { TaskShare } from "../types";
import "./ShareTaskModal.css";

interface Props {
  taskId: number;
  taskTitle: string;
  isOpen: boolean;
  onClose: () => void;
}

export default function ShareTaskModal({ taskId, taskTitle, isOpen, onClose }: Props) {
  const [email, setEmail] = useState("");
  const [permission, setPermission] = useState<"view" | "edit">("view");
  const [shares, setShares] = useState<TaskShare[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      fetchShares();
      setEmail("");
      setPermission("view");
      setError(null);
      setSuccess(null);
    }
  }, [isOpen, taskId]);

  const fetchShares = async () => {
    try {
      const res = await shareApi.getShares(taskId);
      setShares(res.data);
    } catch {
      console.error("Failed to fetch shares");
    }
  };

  const handleShare = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      await shareApi.shareTask(taskId, email, permission);
      setSuccess(`Task shared with ${email}`);
      setEmail("");
      fetchShares();
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } };
      setError(error.response?.data?.detail || "Failed to share task");
    } finally {
      setLoading(false);
    }
  };

  const handleRevoke = async (shareId: number, userEmail: string) => {
    try {
      await shareApi.revokeShare(taskId, shareId);
      setSuccess(`Access revoked for ${userEmail}`);
      fetchShares();
    } catch {
      setError("Failed to revoke access");
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="share-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Share Task</h2>
          <button className="close-button" onClick={onClose}>
            &times;
          </button>
        </div>

        <p className="task-title-label">
          Sharing: <strong>{taskTitle}</strong>
        </p>

        <form className="share-form" onSubmit={handleShare}>
          <div className="form-row">
            <input
              type="email"
              placeholder="Enter email address"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            <select
              value={permission}
              onChange={(e) => setPermission(e.target.value as "view" | "edit")}
            >
              <option value="view">View only</option>
              <option value="edit">Can edit</option>
            </select>
          </div>
          <button type="submit" className="share-button" disabled={loading}>
            {loading ? "Sharing..." : "Share"}
          </button>
        </form>

        {error && <div className="message error">{error}</div>}
        {success && <div className="message success">{success}</div>}

        {shares.length > 0 && (
          <div className="current-shares">
            <h3>Shared with</h3>
            <ul className="shares-list">
              {shares.map((share) => (
                <li key={share.id} className="share-item">
                  <div className="share-info">
                    <span className="share-email">{share.shared_with_email}</span>
                    <span className={`share-permission ${share.permission}`}>
                      {share.permission === "edit" ? "Can edit" : "View only"}
                    </span>
                  </div>
                  <button
                    className="revoke-button"
                    onClick={() => handleRevoke(share.id, share.shared_with_email)}
                  >
                    Revoke
                  </button>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
