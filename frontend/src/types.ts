export interface Task {
  id: number;
  title: string;
  deadline: string | null;
  effort: "low" | "medium" | "high";
  completed: boolean;
}

export interface TaskNote {
  id: number;
  task_id: number;
  content: string;
  created_at: string;
  updated_at: string;
}

export interface TaskAttachment {
  id: number;
  task_id: number;
  filename: string;
  content_type: string;
  file_size: number;
  created_at: string;
}

export interface AISummary {
  summary: string;
  key_points: string[];
  concepts: string[];
  action_items: string[];
  study_tips: string[];
  error: boolean;
}

export interface TaskResource {
  id: number;
  task_id: number;
  title: string;
  url: string;
  description: string | null;
  source: string | null;
  created_at: string;
}

export interface TaskShare {
  id: number;
  task_id: number;
  shared_with_email: string;
  permission: "view" | "edit";
  shared_at: string;
}

export interface SharedTask {
  id: number;
  title: string;
  deadline: string | null;
  effort: "low" | "medium" | "high";
  completed: boolean;
  owner_email: string;
  permission: "view" | "edit";
  shared_at: string;
}

export interface QuestionSolution {
  question_number: string;
  question_text: string;
  approach: string;
  key_concepts: string[];
  solution_steps: string[];
  tips: string;
}

export interface AssignmentSolution {
  id: number;
  task_id: number;
  assignment_filename: string;
  questions: QuestionSolution[];
  created_at: string;
  error?: string | null;
}