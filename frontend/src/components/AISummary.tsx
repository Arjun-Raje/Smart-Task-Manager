import { useState, useEffect } from "react";
import { workspaceApi } from "../api/client";
import type { AISummary as AISummaryType } from "../types";

interface Props {
  taskId: number;
  hasNotes: boolean;
  hasAttachments: boolean;
  canEdit?: boolean;
}

export default function AISummary({ taskId, hasNotes, hasAttachments, canEdit = true }: Props) {
  const [summary, setSummary] = useState<AISummaryType | null>(null);
  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const hasContent = hasNotes || hasAttachments;

  // Fetch saved summary on mount and when attachments change
  useEffect(() => {
    // Clear existing summary immediately when content changes
    setSummary(null);

    const fetchSavedSummary = async () => {
      setInitialLoading(true);
      try {
        const response = await workspaceApi.getSavedSummary(taskId);
        if (response.data) {
          setSummary(response.data);
        } else {
          setSummary(null);
        }
      } catch (err) {
        console.error("Failed to fetch saved summary:", err);
        setSummary(null);
      } finally {
        setInitialLoading(false);
      }
    };

    fetchSavedSummary();
  }, [taskId, hasAttachments, hasNotes]);  // Refetch when content changes

  const generateSummary = async () => {
    setLoading(true);
    setError(null);
    // Clear old summary before generating new one
    setSummary(null);

    try {
      const response = await workspaceApi.generateSummary(taskId);
      setSummary(response.data);
    } catch (err) {
      setError("Failed to generate summary. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  if (initialLoading) {
    return (
      <div className="ai-summary">
        <div className="ai-summary-header">
          <h3>AI Study Guide</h3>
        </div>
        <div className="ai-loading">
          <div className="loading-spinner"></div>
          <p>Loading saved summary...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="ai-summary">
      <div className="ai-summary-header">
        <h3>AI Study Guide</h3>
        {canEdit && (
          <button
            className="generate-btn"
            onClick={generateSummary}
            disabled={loading || !hasContent}
          >
            {loading ? "Analyzing..." : summary ? "Regenerate" : "Generate Study Guide"}
          </button>
        )}
      </div>

      {!hasContent && !summary && (
        <p className="ai-summary-empty">
          Add some notes or attachments first, then generate a detailed AI study guide.
        </p>
      )}

      {loading && (
        <div className="ai-loading">
          <div className="loading-spinner"></div>
          <p>Analyzing your documents and notes...</p>
        </div>
      )}

      {error && <div className="ai-summary-error">{error}</div>}

      {summary && !summary.error && !loading && (
        <div className="ai-summary-content">
          {/* Overview Section */}
          <div className="summary-section">
            <h4>Overview</h4>
            <p>{summary.summary}</p>
          </div>

          {/* Key Points Section */}
          {summary.key_points && summary.key_points.length > 0 && (
            <div className="summary-section">
              <h4>Key Points</h4>
              <ul className="summary-list">
                {summary.key_points.map((point, index) => (
                  <li key={index}>{point}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Important Concepts Section */}
          {summary.concepts && summary.concepts.length > 0 && (
            <div className="summary-section">
              <h4>Important Concepts</h4>
              <ul className="summary-list concepts-list">
                {summary.concepts.map((concept, index) => (
                  <li key={index}>{concept}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Action Items Section */}
          {summary.action_items && summary.action_items.length > 0 && (
            <div className="summary-section">
              <h4>Action Items</h4>
              <ul className="summary-list action-list">
                {summary.action_items.map((item, index) => (
                  <li key={index}>{item}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Study Tips Section */}
          {summary.study_tips && summary.study_tips.length > 0 && (
            <div className="summary-section">
              <h4>Study Tips</h4>
              <ul className="summary-list tips-list">
                {summary.study_tips.map((tip, index) => (
                  <li key={index}>{tip}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {summary && summary.error && (
        <div className="ai-summary-error">{summary.summary}</div>
      )}
    </div>
  );
}
