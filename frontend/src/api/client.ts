import axios from "axios";
import type { Task, TaskNote, TaskAttachment } from "../types";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000",
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
};

export default api;
