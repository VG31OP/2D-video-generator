import { Project, Settings, SystemCapabilities } from '../types';

const API_BASE = '/api';

export async function fetchProjects(): Promise<Project[]> {
  const res = await fetch(`${API_BASE}/projects`);
  if (!res.ok) throw new Error('Failed to fetch projects');
  return res.json();
}

export async function fetchProject(id: string): Promise<Project> {
  const res = await fetch(`${API_BASE}/projects/${id}`);
  if (!res.ok) throw new Error('Failed to fetch project');
  return res.json();
}

export async function createProject(data: {
  topic: string;
  title?: string;
  language?: string;
  art_style?: string;
  duration_seconds?: number;
}): Promise<{ id: string; title: string; status: string }> {
  const res = await fetch(`${API_BASE}/projects`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Failed to create project' }));
    throw new Error(err.detail || 'Failed to create project');
  }
  return res.json();
}

export async function triggerGenerate(id: string): Promise<void> {
  const res = await fetch(`${API_BASE}/projects/${id}/generate`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to start generation');
}

export async function deleteProject(id: string): Promise<void> {
  const res = await fetch(`${API_BASE}/projects/${id}`, { method: 'DELETE' });
  if (!res.ok) throw new Error('Failed to delete project');
}

export async function fetchSettings(): Promise<Settings> {
  const res = await fetch(`${API_BASE}/settings`);
  if (!res.ok) throw new Error('Failed to fetch settings');
  return res.json();
}

export async function fetchSystemHealth(): Promise<SystemCapabilities> {
  const res = await fetch(`${API_BASE}/settings/health`);
  if (!res.ok) throw new Error('Failed to fetch system capabilities');
  return res.json();
}

export async function testAllProviders(): Promise<any> {
  const res = await fetch(`${API_BASE}/settings/test-all`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to test providers');
  return res.json();
}

export async function updateSettings(settings: Partial<Settings>): Promise<void> {
  const res = await fetch(`${API_BASE}/settings`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(settings),
  });
  if (!res.ok) throw new Error('Failed to update settings');
}

export async function testOllamaConnection(url: string): Promise<{ connected: boolean; models?: string[]; error?: string }> {
  const res = await fetch(`${API_BASE}/settings/test-ollama?url=${encodeURIComponent(url)}`);
  return res.json();
}

export function subscribeToProjectProgress(
  projectId: string,
  onProgress: (data: any) => void
): () => void {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const wsUrl = `${protocol}//${window.location.host}/ws/projects/${projectId}`;
  
  let ws: WebSocket | null = null;
  let isCancelled = false;

  const connect = () => {
    if (isCancelled) return;
    try {
      ws = new WebSocket(wsUrl);
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          onProgress(data);
        } catch (e) {
          console.error('WS parse error', e);
        }
      };
      ws.onerror = (e) => {
        console.warn('WS error', e);
      };
      ws.onclose = () => {
        if (!isCancelled) {
          setTimeout(connect, 2000);
        }
      };
    } catch (e) {
      console.error('WS connect error', e);
    }
  };

  connect();

  return () => {
    isCancelled = true;
    if (ws) {
      ws.close();
    }
  };
}
