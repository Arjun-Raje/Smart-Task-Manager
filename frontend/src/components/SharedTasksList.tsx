import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { shareApi } from "../api/client";
import type { SharedTask } from "../types";
import "./SharedTasksList.css";

export default function SharedTasksList() {
  const navigate = useNavigate();
  const [sharedTasks, setSharedTasks] = useState<SharedTask[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSharedTasks();
  }, []);

  const fetchSharedTasks = async () => {
    try {
      const res = await shareApi.getSharedWithMe();
      setSharedTasks(res.data);
    } catch (err) {
      console.error("Failed to fetch shared tasks:", err);
    } finally {
      setLoading(false);
    }
  };

  const openWorkspace = (taskId: number) => {
    navigate(`/tasks/${taskId}`);
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString();
  };

  if (loading) {
    return (
      <div className="shared-tasks-card">
        <h2>Shared with Me</h2>
        <p className="loading-state">Loading...</p>
      </div>
    );
  }

  return (
    <div className="shared-tasks-card">
      <h2>
        Shared with Me
        {sharedTasks.length > 0 && (
          <span className="shared-count">{sharedTasks.length}</span>
        )}
      </h2>

      {sharedTasks.length === 0 ? (
        <p className="empty-state">No tasks have been shared with you yet.</p>
      ) : (
        <ul className="shared-tasks-list">
          {sharedTasks.map((task) => (
            <li
              key={task.id}
              className={`shared-task-item ${task.completed ? "completed" : ""}`}
              onClick={() => openWorkspace(task.id)}
            >
              <div className="shared-task-content">
                <div className="shared-task-title">{task.title}</div>
                <div className="shared-task-meta">
                  <span className="shared-by">from {task.owner_email}</span>
                  <span className={`permission-badge ${task.permission}`}>
                    {task.permission === "edit" ? "Can edit" : "View only"}
                  </span>
                </div>
              </div>
              {task.deadline && (
                <span className="shared-task-deadline">
                  Due {formatDate(task.deadline)}
                </span>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
