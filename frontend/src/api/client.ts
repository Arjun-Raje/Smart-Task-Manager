import axios from "axios";
import type { Task, TaskNote, TaskAttachment, AISummary, TaskResource, TaskShare, SharedTask, AssignmentSolution } from "../types";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://127.0.0.1:8000",
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const workspaceApi = {
  getTask: (taskId: number) =>
    api.get<Task>(`/tasks/${taskId}`),

  getNotes: (taskId: number) =>
    api.get<TaskNote | null>(`/tasks/${taskId}/workspace/notes`),

  updateNotes: (taskId: number, content: string) =>
    api.put<TaskNote>(`/tasks/${taskId}/workspace/notes`, { content }),

  getAttachments: (taskId: number) =>
    api.get<TaskAttachment[]>(`/tasks/${taskId}/workspace/attachments`),

  uploadAttachment: (taskId: number, file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return api.post<TaskAttachment>(`/tasks/${taskId}/workspace/attachments`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },

  downloadAttachment: (taskId: number, attachmentId: number) =>
    api.get(`/tasks/${taskId}/workspace/attachments/${attachmentId}/download`, {
      responseType: "blob",
    }),

  deleteAttachment: (taskId: number, attachmentId: number) =>
    api.delete(`/tasks/${taskId}/workspace/attachments/${attachmentId}`),

  getSavedSummary: (taskId: number) =>
    api.get<AISummary | null>(`/tasks/${taskId}/workspace/summary`),

  deleteSummary: (taskId: number) =>
    api.delete(`/tasks/${taskId}/workspace/summary`),

  generateSummary: (taskId: number) =>
    api.post<AISummary>(`/tasks/${taskId}/workspace/summary/generate`),

  getResources: (taskId: number) =>
    api.get<TaskResource[]>(`/tasks/${taskId}/workspace/resources`),

  deleteResources: (taskId: number) =>
    api.delete(`/tasks/${taskId}/workspace/resources`),

  generateResources: (taskId: number) =>
    api.post<{ resources: TaskResource[]; error: string | null }>(`/tasks/${taskId}/workspace/resources/generate`),

  getAssignmentSolutions: (taskId: number) =>
    api.get<AssignmentSolution[]>(`/tasks/${taskId}/workspace/assignments`),

  solveAssignment: (taskId: number, file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return api.post<AssignmentSolution>(`/tasks/${taskId}/workspace/assignments/solve`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },

  deleteAssignmentSolution: (taskId: number, solutionId: number) =>
    api.delete(`/tasks/${taskId}/workspace/assignments/${solutionId}`),
};

export interface TaskPermission {
  permission: "owner" | "view" | "edit";
  owner_email: string;
  is_owner: boolean;
}

export const shareApi = {
  shareTask: (taskId: number, email: string, permission: string) =>
    api.post<TaskShare>(`/tasks/${taskId}/share`, { email, permission }),

  getShares: (taskId: number) =>
    api.get<TaskShare[]>(`/tasks/${taskId}/shares`),

  revokeShare: (taskId: number, shareId: number) =>
    api.delete(`/tasks/${taskId}/share/${shareId}`),

  getSharedWithMe: () =>
    api.get<SharedTask[]>('/shared-with-me'),

  getMyPermission: (taskId: number) =>
    api.get<TaskPermission>(`/tasks/${taskId}/my-permission`),
};

export default api;
