/**
 * mkh_Manus Unified API Client
 * 
 * This client handles all communication with the backend.
 * It uses a flexible API_BASE that can be configured via environment variables.
 */

// @ts-ignore - import.meta is available in Vite
const API_BASE = (import.meta?.env?.VITE_API_BASE) ?? "/api/v1";

console.log(`[API] Initialized with base: ${API_BASE}`);

async function request(path: string, options: RequestInit = {}) {
  const url = `${API_BASE}${path}`;
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || `Request failed with status ${response.status}`);
  }

  return response.json();
}

// --- Settings & Keys ---

export async function getSettings() {
  return request('/settings/keys');
}

export async function setApiKeys(keys: Record<string, string>) {
  return request('/settings/keys', {
    method: 'POST',
    body: JSON.stringify(keys),
  });
}

// --- Tasks ---

export interface TaskSummary {
  id: string;
  goal: string;
  status: 'waiting' | 'running' | 'completed' | 'failed' | 'cancelled';
  progress: number;
  steps_done: number;
  steps_estimate: number;
  elapsed_seconds: number;
  eta_seconds: number;
  token_total: number;
  token_budget: number;
  last_error?: string;
}

export interface TaskEvent {
  id: number;
  ts: string;
  level: 'info' | 'warning' | 'error' | 'success';
  kind: string;
  message: string;
  data?: any;
}

export async function listTasks(): Promise<TaskSummary[]> {
  return request('/tasks');
}

export async function createTask(goal: string, projectPath: string = ".", tokenBudget: number = 1000000) {
  return request('/tasks', {
    method: 'POST',
    body: JSON.stringify({ goal, project_path: projectPath, token_budget: tokenBudget }),
  });
}

export async function getTask(id: string): Promise<TaskSummary> {
  return request(`/tasks/${id}`);
}

export async function cancelTask(id: string) {
  return request(`/tasks/${id}/cancel`, { method: 'POST' });
}

export async function getEvents(taskId: string, after: number = 0): Promise<{ events: TaskEvent[] }> {
  return request(`/tasks/${taskId}/events?after=${after}`);
}

// --- Workspace ---

export async function listWorkspace(path: string = ".") {
  return request(`/workspace/tree?path=${encodeURIComponent(path)}`);
}

export async function readWorkspaceFile(path: string) {
  return request(`/workspace/file?path=${encodeURIComponent(path)}`);
}

async function upload(endpoint: string, file: File) {
  const formData = new FormData();
  formData.append(endpoint.includes('image') ? 'image' : endpoint.includes('video') ? 'video' : endpoint.includes('audio') ? 'audio' : 'file', file);
  
  const response = await fetch(`${API_BASE}${endpoint}`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error(`Upload failed: ${response.statusText}`);
  }

  return response.json();
}

export async function uploadFile(file: File) { return upload('/workspace/upload', file); }
export async function uploadImage(file: File) { return upload('/workspace/upload-image', file); }
export async function uploadVideo(file: File) { return upload('/workspace/upload-video', file); }
export async function uploadAudio(file: File) { return upload('/workspace/upload-audio', file); }
