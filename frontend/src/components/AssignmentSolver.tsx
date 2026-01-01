import { useState, useEffect, useRef } from "react";
import { workspaceApi } from "../api/client";
import type { AssignmentSolution, QuestionSolution } from "../types";

interface Props {
  taskId: number;
  hasContent: boolean;
  canEdit?: boolean;
}

export default function AssignmentSolver({ taskId, hasContent, canEdit = true }: Props) {
  const [solutions, setSolutions] = useState<AssignmentSolution[]>([]);
  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedQuestions, setExpandedQuestions] = useState<Set<string>>(new Set());
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Fetch saved solutions on mount
  useEffect(() => {
    const fetchSolutions = async () => {
      setInitialLoading(true);
      try {
        const response = await workspaceApi.getAssignmentSolutions(taskId);
        if (response.data) {
          setSolutions(response.data);
        }
      } catch (err) {
        console.error("Failed to fetch assignment solutions:", err);
      } finally {
        setInitialLoading(false);
      }
    };

    fetchSolutions();
  }, [taskId]);

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setLoading(true);
    setError(null);

    try {
      const response = await workspaceApi.solveAssignment(taskId, file);
      if (response.data.error) {
        setError(response.data.error);
      } else {
        setSolutions(prev => [response.data, ...prev]);
        // Auto-expand all questions for new solution
        const newExpanded = new Set<string>();
        response.data.questions.forEach((_, idx) => {
          newExpanded.add(`${response.data.id}-${idx}`);
        });
        setExpandedQuestions(prev => new Set([...prev, ...newExpanded]));
      }
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : "Failed to analyze assignment. Please try again.";
      setError(errorMessage);
    } finally {
      setLoading(false);
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  };

  const handleDelete = async (solutionId: number) => {
    try {
      await workspaceApi.deleteAssignmentSolution(taskId, solutionId);
      setSolutions(prev => prev.filter(s => s.id !== solutionId));
    } catch (err) {
      console.error("Failed to delete solution:", err);
    }
  };

  const toggleQuestion = (key: string) => {
    setExpandedQuestions(prev => {
      const newSet = new Set(prev);
      if (newSet.has(key)) {
        newSet.delete(key);
      } else {
        newSet.add(key);
      }
      return newSet;
    });
  };

  const renderQuestion = (question: QuestionSolution, solutionId: number, index: number) => {
    const key = `${solutionId}-${index}`;
    const isExpanded = expandedQuestions.has(key);

    return (
      <div key={key} className="question-card">
        <button
          className="question-header"
          onClick={() => toggleQuestion(key)}
        >
          <div className="question-number">Q{question.question_number}</div>
          <div className="question-text">{question.question_text}</div>
          <span className={`expand-icon ${isExpanded ? "expanded" : ""}`}>▼</span>
        </button>

        {isExpanded && (
          <div className="question-content">
            <div className="solution-section">
              <h5>Approach</h5>
              <p>{question.approach}</p>
            </div>

            {question.key_concepts && question.key_concepts.length > 0 && (
              <div className="solution-section concepts">
                <h5>Key Concepts</h5>
                <div className="concept-tags">
                  {question.key_concepts.map((concept, i) => (
                    <span key={i} className="concept-tag">{concept}</span>
                  ))}
                </div>
              </div>
            )}

            {question.solution_steps && question.solution_steps.length > 0 && (
              <div className="solution-section steps">
                <h5>Solution Steps</h5>
                <ol className="steps-list">
                  {question.solution_steps.map((step, i) => (
                    <li key={i}>{step}</li>
                  ))}
                </ol>
              </div>
            )}

            {question.tips && (
              <div className="solution-section tips">
                <h5>Tips</h5>
                <p>{question.tips}</p>
              </div>
            )}
          </div>
        )}
      </div>
    );
  };

  if (initialLoading) {
    return (
      <div className="assignment-solver">
        <div className="assignment-header">
          <h3>Assignment Solver</h3>
        </div>
        <div className="assignment-loading">
          <div className="loading-spinner small"></div>
          <p>Loading solutions...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="assignment-solver">
      <div className="assignment-header">
        <h3>Assignment Solver</h3>
        {canEdit && (
          <label className={`upload-assignment-btn ${loading ? "loading" : ""}`}>
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,image/*"
              onChange={handleFileSelect}
              disabled={loading || !hasContent}
              hidden
            />
            {loading ? (
              <span className="btn-loading">Analyzing...</span>
            ) : (
              <>
                <span className="upload-icon">📝</span>
                Upload Assignment
              </>
            )}
          </label>
        )}
      </div>

      {!hasContent && solutions.length === 0 && (
        <p className="assignment-empty">
          Add notes or study materials first, then upload an assignment to get AI-powered solution approaches.
        </p>
      )}

      {loading && (
        <div className="assignment-loading">
          <div className="loading-spinner"></div>
          <p>Analyzing your assignment and generating solution approaches...</p>
          <p className="loading-hint">This may take a moment for longer assignments.</p>
        </div>
      )}

      {error && <div className="assignment-error">{error}</div>}

      {!loading && solutions.length > 0 && (
        <div className="solutions-list">
          {solutions.map(solution => (
            <div key={solution.id} className="solution-card">
              <div className="solution-header">
                <div className="solution-info">
                  <span className="file-icon">📄</span>
                  <span className="file-name">{solution.assignment_filename}</span>
                  <span className="question-count">
                    {solution.questions.length} question{solution.questions.length !== 1 ? "s" : ""}
                  </span>
                </div>
                {canEdit && (
                  <button
                    className="delete-solution-btn"
                    onClick={() => handleDelete(solution.id)}
                    title="Delete solution"
                  >
                    ×
                  </button>
                )}
              </div>

              <div className="questions-list">
                {solution.questions.map((q, idx) => renderQuestion(q, solution.id, idx))}
              </div>
            </div>
          ))}
        </div>
      )}

      {!loading && hasContent && solutions.length === 0 && !error && (
        <p className="assignment-hint">
          Upload a PDF or image of your assignment to get step-by-step guidance on solving each question.
        </p>
      )}
    </div>
  );
}
