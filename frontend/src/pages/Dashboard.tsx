import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/client";
import { useAuth } from "../auth/AuthContext";
import type { Task } from "../types";
import TaskForm from "../components/TaskForm";
import TaskList from "../components/TaskList";
import TaskCalendar from "../components/TaskCalendar";
import SuggestionsList from "../components/SuggestionsList";
import "./Dashboard.css";

type ViewMode = "list" | "calendar";

export default function Dashboard() {
  const { logout } = useAuth();
  const navigate = useNavigate();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [view, setView] = useState<ViewMode>("list");

  const fetchTasks = async () => {
    const res = await api.get("/tasks");
    setTasks(res.data);
  };

  useEffect(() => {
    fetchTasks();
  }, []);

  const completedCount = tasks.filter((t) => t.completed).length;
  const pendingCount = tasks.filter((t) => !t.completed).length;

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>Task Dashboard</h1>
        <div className="header-actions">
          <div className="view-toggle">
            <button
              className={`view-button ${view === "list" ? "active" : ""}`}
              onClick={() => setView("list")}
            >
              List
            </button>
            <button
              className={`view-button ${view === "calendar" ? "active" : ""}`}
              onClick={() => setView("calendar")}
            >
              Calendar
            </button>
          </div>
          <button className="logout-button" onClick={logout}>
            Logout
          </button>
        </div>
      </header>

      <div className="dashboard-content">
        <div className="main-section">
          <TaskForm onTaskCreated={fetchTasks} />
          {view === "list" ? (
            <TaskList tasks={tasks} refreshTasks={fetchTasks} />
          ) : (
            <TaskCalendar tasks={tasks} onTaskClick={(task) => navigate(`/tasks/${task.id}`)} />
          )}
        </div>

        <aside className="sidebar">
          <div className="stats-card">
            <h2>Overview</h2>
            <div className="stats-grid">
              <div className="stat-item">
                <div className="stat-value">{tasks.length}</div>
                <div className="stat-label">Total Tasks</div>
              </div>
              <div className="stat-item">
                <div className="stat-value">{pendingCount}</div>
                <div className="stat-label">Pending</div>
              </div>
              <div className="stat-item">
                <div className="stat-value">{completedCount}</div>
                <div className="stat-label">Completed</div>
              </div>
              <div className="stat-item">
                <div className="stat-value">
                  {tasks.length > 0
                    ? Math.round((completedCount / tasks.length) * 100)
                    : 0}
                  %
                </div>
                <div className="stat-label">Progress</div>
              </div>
            </div>
          </div>

          <SuggestionsList onTaskChange={fetchTasks} />
        </aside>
      </div>
    </div>
  );
}
