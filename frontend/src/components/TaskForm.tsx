import { useState } from "react";
import api from "../api/client";

interface Props {
  onTaskCreated: () => void;
}

export default function TaskForm({ onTaskCreated }: Props) {
  const [title, setTitle] = useState("");
  const [deadline, setDeadline] = useState("");
  const [effort, setEffort] = useState<"low" | "medium" | "high">("medium");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await api.post("/tasks", {
      title,
      deadline: deadline || null,
      effort,
    });
    setTitle("");
    setDeadline("");
    setEffort("medium");
    onTaskCreated();
  };

  return (
    <div className="task-form-card">
      <h2>Add New Task</h2>
      <form className="task-form" onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="What needs to be done?"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
        />
        <div className="task-form-row">
          <input
            type="datetime-local"
            value={deadline}
            onChange={(e) => setDeadline(e.target.value)}
          />
          <select
            value={effort}
            onChange={(e) => setEffort(e.target.value as "low" | "medium" | "high")}
          >
            <option value="low">Low Effort</option>
            <option value="medium">Medium Effort</option>
            <option value="high">High Effort</option>
          </select>
        </div>
        <button type="submit" className="add-task-button">
          Add Task
        </button>
      </form>
    </div>
  );
}
