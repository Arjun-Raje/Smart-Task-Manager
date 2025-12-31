import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { workspaceApi, shareApi, type TaskPermission } from "../api/client";
import type { Task, TaskAttachment, TaskNote } from "../types";
import NotesEditor from "../components/NotesEditor";
import FileUpload from "../components/FileUpload";
import AISummary from "../components/AISummary";
import ResourceSuggestions from "../components/ResourceSuggestions";
import ShareTaskModal from "../components/ShareTaskModal";
import "./TaskWorkspace.css";

export default function TaskWorkspace() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [task, setTask] = useState<Task | null>(null);
  const [attachments, setAttachments] = useState<TaskAttachment[]>([]);
  const [notes, setNotes] = useState<TaskNote | null>(null);
  const [permission, setPermission] = useState<TaskPermission | null>(null);
  const [showShareModal, setShowShareModal] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const taskId = parseInt(id || "0", 10);

  const fetchTask = async () => {
    try {
      const response = await workspaceApi.getTask(taskId);
      setTask(response.data);
    } catch (err) {
      setError("Task not found");
    }
  };

  const fetchAttachments = async () => {
    try {
      const response = await workspaceApi.getAttachments(taskId);
      setAttachments(response.data);
    } catch (err) {
      console.error("Failed to fetch attachments:", err);
    }
  };

  const fetchNotes = async () => {
    try {
      const response = await workspaceApi.getNotes(taskId);
      setNotes(response.data);
    } catch (err) {
      console.error("Failed to fetch notes:", err);
    }
  };

  const fetchPermission = async () => {
    try {
      const response = await shareApi.getMyPermission(taskId);
      setPermission(response.data);
    } catch (err) {
      console.error("Failed to fetch permission:", err);
    }
  };

  useEffect(() => {
    if (!taskId) {
      setError("Invalid task ID");
      setLoading(false);
      return;
    }

    const loadData = async () => {
      setLoading(true);
      await Promise.all([fetchTask(), fetchAttachments(), fetchNotes(), fetchPermission()]);
      setLoading(false);
    };

    loadData();
  }, [taskId]);

  const canEdit = permission?.is_owner || permission?.permission === "edit";

  if (loading) {
    return (
      <div className="workspace-container">
        <div className="loading">Loading workspace...</div>
      </div>
    );
  }

  if (error || !task) {
    return (
      <div className="workspace-container">
        <div className="error-card">
          <h2>Error</h2>
          <p>{error || "Task not found"}</p>
          <button onClick={() => navigate("/")} className="back-btn">
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  const formatDeadline = (deadline: string | null) => {
    if (!deadline) return "No deadline";
    const date = new Date(deadline);
    return date.toLocaleDateString("en-US", {
      weekday: "long",
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  };

  const getEffortLabel = (effort: string) => {
    switch (effort) {
      case "low":
        return "Low Effort";
      case "medium":
        return "Medium Effort";
      case "high":
        return "High Effort";
      default:
        return effort;
    }
  };

  return (
    <div className="workspace-container">
      <header className="workspace-header">
        <button onClick={() => navigate("/")} className="back-btn">
          ← Back to Dashboard
        </button>
        <h1>Task Workspace</h1>
        {permission?.is_owner && (
          <button className="share-workspace-btn" onClick={() => setShowShareModal(true)}>
            Share
          </button>
        )}
      </header>

      <div className="workspace-content">
        <div className="task-details-card">
          <div className="task-header">
            <h2 className={task.completed ? "completed" : ""}>{task.title}</h2>
            <div className="task-badges">
              {!permission?.is_owner && permission && (
                <span className="shared-badge">
                  Shared by {permission.owner_email}
                  <span className={`permission-level ${permission.permission}`}>
                    {permission.permission === "edit" ? "Can edit" : "View only"}
                  </span>
                </span>
              )}
              <span className={`status-badge ${task.completed ? "done" : "pending"}`}>
                {task.completed ? "Completed" : "In Progress"}
              </span>
            </div>
          </div>
          <div className="task-meta">
            <span className="deadline">📅 {formatDeadline(task.deadline)}</span>
            <span className={`effort ${task.effort}`}>{getEffortLabel(task.effort)}</span>
          </div>
        </div>

        <div className="workspace-grid">
          <div className="notes-card">
            <NotesEditor taskId={taskId} onNotesChange={fetchNotes} canEdit={canEdit} />
          </div>

          <div className="attachments-card">
            <FileUpload
              taskId={taskId}
              attachments={attachments}
              onAttachmentsChange={fetchAttachments}
              canEdit={canEdit}
            />
          </div>
        </div>

        <div className="ai-summary-card">
          <AISummary
            taskId={taskId}
            hasNotes={!!notes && !!notes.content.trim()}
            hasAttachments={attachments.length > 0}
            canEdit={canEdit}
          />
        </div>

        <div className="resources-card">
          <ResourceSuggestions
            taskId={taskId}
            hasContent={!!notes?.content.trim() || attachments.length > 0}
            canEdit={canEdit}
          />
        </div>
      </div>

      {showShareModal && task && (
        <ShareTaskModal
          taskId={taskId}
          taskTitle={task.title}
          isOpen={showShareModal}
          onClose={() => setShowShareModal(false)}
        />
      )}
    </div>
  );
}
