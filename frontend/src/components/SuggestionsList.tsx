import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import type { Task } from "../types";
import api from "../api/client";

interface Props {
  onTaskChange?: () => void;
}

export default function SuggestionsList({ onTaskChange }: Props) {
  const navigate = useNavigate();
  const [suggestions, setSuggestions] = useState<Task[]>([]);

  const fetchSuggestions = async () => {
    try {
      const res = await api.get("/tasks/suggestions");
      setSuggestions(res.data);
    } catch {
      setSuggestions([]);
    }
  };

  useEffect(() => {
    fetchSuggestions();
  }, []);

  useEffect(() => {
    if (onTaskChange) {
      fetchSuggestions();
    }
  }, [onTaskChange]);

  const formatDeadline = (deadline: string | null) => {
    if (!deadline) return null;
    const date = new Date(deadline);
    const now = new Date();
    const diffHours = (date.getTime() - now.getTime()) / (1000 * 60 * 60);

    let className = "";
    if (diffHours < 0) className = "overdue";
    else if (diffHours < 24) className = "soon";

    return (
      <span className={`task-deadline ${className}`}>
        {date.toLocaleDateString()}
      </span>
    );
  };

  return (
    <div className="suggestions-card">
      <h2>Focus On These</h2>
      {suggestions.length === 0 ? (
        <p className="empty-state">No suggestions yet. Add some tasks!</p>
      ) : (
        <ul className="suggestions-list">
          {suggestions.map((task, index) => (
            <li
              key={task.id}
              className="suggestion-item clickable"
              onClick={() => navigate(`/tasks/${task.id}`)}
            >
              <span className="suggestion-rank">{index + 1}</span>
              <div className="suggestion-content">
                <div className="suggestion-title">{task.title}</div>
                <div className="suggestion-meta">
                  {task.effort && (
                    <span className={`task-effort ${task.effort}`}>
                      {task.effort}
                    </span>
                  )}
                  {formatDeadline(task.deadline)}
                </div>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
