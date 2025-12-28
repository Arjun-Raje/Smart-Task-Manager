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