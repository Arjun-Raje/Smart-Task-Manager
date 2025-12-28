import { useState, useEffect, useRef } from "react";
import { workspaceApi } from "../api/client";

interface Props {
  taskId: number;
}

export default function NotesEditor({ taskId }: Props) {
  const [content, setContent] = useState("");
  const [saveStatus, setSaveStatus] = useState<"idle" | "saving" | "saved" | "error">("idle");
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  const timeoutRef = useRef<number | null>(null);
  const isInitialLoad = useRef(true);

  useEffect(() => {
    const fetchNotes = async () => {
      try {
        const response = await workspaceApi.getNotes(taskId);
        if (response.data) {
          setContent(response.data.content);
        }
        isInitialLoad.current = false;
      } catch (error) {
        console.error("Failed to fetch notes:", error);
        isInitialLoad.current = false;
      }
    };
    fetchNotes();
  }, [taskId]);

  useEffect(() => {
    if (isInitialLoad.current) return;

    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    setSaveStatus("idle");

    timeoutRef.current = window.setTimeout(async () => {
      setSaveStatus("saving");
      try {
        await workspaceApi.updateNotes(taskId, content);
        setSaveStatus("saved");
        setLastSaved(new Date());
      } catch (error) {
        console.error("Failed to save notes:", error);
        setSaveStatus("error");
      }
    }, 1000);

    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [content, taskId]);

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  };

  return (
    <div className="notes-editor">
      <div className="notes-header">
        <h3>Notes</h3>
        <span className={`save-status ${saveStatus}`}>
          {saveStatus === "saving" && "Saving..."}
          {saveStatus === "saved" && lastSaved && `Saved at ${formatTime(lastSaved)}`}
          {saveStatus === "error" && "Failed to save"}
        </span>
      </div>
      <textarea
        className="notes-textarea"
        value={content}
        onChange={(e) => setContent(e.target.value)}
        placeholder="Write your notes here... They will auto-save as you type."
      />
    </div>
  );
}
