import { useState } from "react";
import { useNavigate } from "react-router-dom";
import type { Task } from "../types";
import api from "../api/client";
import ShareTaskModal from "./ShareTaskModal";

interface Props {
  tasks: Task[];
  refreshTasks: () => void;
}

export default function TaskList({ tasks, refreshTasks }: Props) {
  const navigate = useNavigate();
  const [shareModalTask, setShareModalTask] = useState<Task | null>(null);

  const openShareModal = (task: Task, e: React.MouseEvent) => {
    e.stopPropagation();
    setShareModalTask(task);
  };

  const toggleComplete = async (task: Task, e: React.MouseEvent) => {
    e.stopPropagation();
    await api.put(`/tasks/${task.id}`, { completed: !task.completed });
    refreshTasks();
  };

  const deleteTask = async (id: number, e: React.MouseEvent) => {
    e.stopPropagation();
    await api.delete(`/tasks/${id}`);
    refreshTasks();
  };

  const openWorkspace = (taskId: number) => {
    navigate(`/tasks/${taskId}`);
  };

  const formatDeadline = (deadline: string | null) => {
    if (!deadline) return null;
    const date = new Date(deadline);
    const now = new Date();
    const diffHours = (date.getTime() - now.getTime()) / (1000 * 60 * 60);

    let className = "";
    let label = date.toLocaleDateString();

    if (diffHours < 0) {
      className = "overdue";
      label = "Overdue";
    } else if (diffHours < 24) {
      className = "soon";
      label = "Due today";
    } else if (diffHours < 48) {
      label = "Due tomorrow";
    }

    return <span className={`task-deadline ${className}`}>{label}</span>;
  };

  const pendingTasks = tasks.filter((t) => !t.completed);
  const completedTasks = tasks.filter((t) => t.completed);

  return (
    <div className="task-list-card">
      <h2>
        Your Tasks
        <span className="task-count">{tasks.length}</span>
      </h2>

      {tasks.length === 0 ? (
        <p className="empty-state">No tasks yet. Create one above!</p>
      ) : (
        <ul className="task-list">
          {pendingTasks.map((task) => (
            <li
              key={task.id}
              className="task-item clickable"
              onClick={() => openWorkspace(task.id)}
            >
              <button
                className={`task-checkbox ${task.completed ? "checked" : ""}`}
                onClick={(e) => toggleComplete(task, e)}
                aria-label={task.completed ? "Mark incomplete" : "Mark complete"}
              />
              <div className="task-content">
                <div className="task-title">{task.title}</div>
                <div className="task-meta">
                  {task.effort && (
                    <span className={`task-effort ${task.effort}`}>
                      {task.effort}
                    </span>
                  )}
                  {formatDeadline(task.deadline)}
                </div>
              </div>
              <button
                className="share-button"
                onClick={(e) => openShareModal(task, e)}
              >
                Share
              </button>
              <button
                className="delete-button"
                onClick={(e) => deleteTask(task.id, e)}
              >
                Delete
              </button>
            </li>
          ))}

          {completedTasks.length > 0 && pendingTasks.length > 0 && (
            <li className="task-divider" style={{
              borderTop: '1px solid rgba(255,255,255,0.1)',
              margin: '0.5rem 0',
              listStyle: 'none'
            }} />
          )}

          {completedTasks.map((task) => (
            <li
              key={task.id}
              className="task-item completed clickable"
              onClick={() => openWorkspace(task.id)}
            >
              <button
                className="task-checkbox checked"
                onClick={(e) => toggleComplete(task, e)}
                aria-label="Mark incomplete"
              />
              <div className="task-content">
                <div className="task-title">{task.title}</div>
                <div className="task-meta">
                  {task.effort && (
                    <span className={`task-effort ${task.effort}`}>
                      {task.effort}
                    </span>
                  )}
                </div>
              </div>
              <button
                className="share-button"
                onClick={(e) => openShareModal(task, e)}
              >
                Share
              </button>
              <button
                className="delete-button"
                onClick={(e) => deleteTask(task.id, e)}
              >
                Delete
              </button>
            </li>
          ))}
        </ul>
      )}

      {shareModalTask && (
        <ShareTaskModal
          taskId={shareModalTask.id}
          taskTitle={shareModalTask.title}
          isOpen={true}
          onClose={() => setShareModalTask(null)}
        />
      )}
    </div>
  );
}
