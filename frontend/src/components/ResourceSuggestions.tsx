import { useState, useEffect } from "react";
import { workspaceApi } from "../api/client";
import type { TaskResource } from "../types";

interface Props {
  taskId: number;
  hasContent: boolean;
  canEdit?: boolean;
}

export default function ResourceSuggestions({ taskId, hasContent, canEdit = true }: Props) {
  const [resources, setResources] = useState<TaskResource[]>([]);
  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch saved resources on mount and when content changes
  useEffect(() => {
    // Clear existing resources immediately when content changes
    setResources([]);

    const fetchResources = async () => {
      setInitialLoading(true);
      try {
        const response = await workspaceApi.getResources(taskId);
        if (response.data) {
          setResources(response.data);
        } else {
          setResources([]);
        }
      } catch (err) {
        console.error("Failed to fetch resources:", err);
        setResources([]);
      } finally {
        setInitialLoading(false);
      }
    };

    fetchResources();
  }, [taskId, hasContent]);  // Refetch when content changes

  const generateResources = async () => {
    setLoading(true);
    setError(null);
    // Clear old resources before generating new ones
    setResources([]);

    try {
      const response = await workspaceApi.generateResources(taskId);
      if (response.data.error) {
        setError(response.data.error);
      } else {
        setResources(response.data.resources);
      }
    } catch (err) {
      setError("Failed to find resources. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const getSourceIcon = (source: string | null) => {
    if (!source) return "🔗";
    const s = source.toLowerCase();
    if (s.includes("khan")) return "🎓";
    if (s.includes("youtube")) return "📺";
    if (s.includes("wikipedia")) return "📚";
    if (s.includes("coursera") || s.includes("edx")) return "🎯";
    if (s.includes("quizlet")) return "📝";
    if (s.includes("github")) return "💻";
    return "🔗";
  };

  if (initialLoading) {
    return (
      <div className="resources-section">
        <div className="resources-header">
          <h3>Suggested Resources</h3>
        </div>
        <div className="resources-loading">
          <div className="loading-spinner small"></div>
          <p>Loading resources...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="resources-section">
      <div className="resources-header">
        <h3>Suggested Resources</h3>
        {canEdit && (
          <button
            className="refresh-btn"
            onClick={generateResources}
            disabled={loading || !hasContent}
            title={resources.length > 0 ? "Find new resources" : "Find resources"}
          >
            {loading ? (
              <span className="btn-loading">Finding...</span>
            ) : (
              <>
                <span className="refresh-icon">↻</span>
                {resources.length > 0 ? "Refresh" : "Find Resources"}
              </>
            )}
          </button>
        )}
      </div>

      {!hasContent && resources.length === 0 && (
        <p className="resources-empty">
          Add notes or attachments, then click "Find Resources" to get helpful study materials.
        </p>
      )}

      {loading && (
        <div className="resources-loading">
          <div className="loading-spinner small"></div>
          <p>Searching for relevant resources...</p>
        </div>
      )}

      {error && <div className="resources-error">{error}</div>}

      {!loading && resources.length > 0 && (
        <ul className="resources-list">
          {resources.map((resource) => (
            <li key={resource.id} className="resource-item">
              <a
                href={resource.url}
                target="_blank"
                rel="noopener noreferrer"
                className="resource-link"
              >
                <span className="resource-icon">{getSourceIcon(resource.source)}</span>
                <div className="resource-content">
                  <span className="resource-title">{resource.title}</span>
                  {resource.description && (
                    <span className="resource-description">{resource.description}</span>
                  )}
                  <span className="resource-source">
                    {resource.source || new URL(resource.url).hostname}
                  </span>
                </div>
                <span className="external-icon">↗</span>
              </a>
            </li>
          ))}
        </ul>
      )}

      {!loading && hasContent && resources.length === 0 && !error && (
        <p className="resources-hint">
          Click "Find Resources" to discover helpful study materials related to your assignment.
        </p>
      )}
    </div>
  );
}
