const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8443';

async function request<T>(method: string, path: string, body?: unknown): Promise<T> {
  const opts: RequestInit = {
    method,
    headers: { 'Content-Type': 'application/json' },
  };
  const token = localStorage.getItem('stalker_token');
  if (token) {
    (opts.headers as Record<string, string>)['Authorization'] = `Bearer ${token}`;
  }
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(`${API_BASE}${path}`, opts);
  if (!res.ok) throw new Error(`${res.status}`);
  return res.json();
}

export const api = {
  login: (username: string, password: string) =>
    request<{ access_token: string }>('POST', '/api/auth/login', { username, password }),

  getDashboardStats: () => request<DashboardStats>('GET', '/api/dashboard/stats'),
  getCampaigns: () => request<Campaign[]>('GET', '/api/campaigns'),
  getCampaign: (id: string) => request<Campaign>('GET', `/api/campaigns/${id}`),
  createCampaign: (data: { name: string; description: string; duration_hours: number }) =>
    request<Campaign>('POST', '/api/campaigns', data),

  getEvents: () => request<TrainingEvent[]>('GET', '/api/events'),
  getLocations: () => request<LocationEvent[]>('GET', '/api/locations'),
  getBrowserInfo: () => request<BrowserInfoEntry[]>('GET', '/api/browser-info'),
  getReport: (campaignId: string, format: string) =>
    request<Record<string, unknown>>('GET', `/api/reports/${campaignId}?format=${format}`),
};

/* ── Types ────────────────────────────────────────────────────────── */

export interface DashboardStats {
  active_campaigns: number;
  total_campaigns: number;
  total_participants: number;
  location_granted: number;
  location_denied: number;
  camera_granted: number;
  camera_denied: number;
  recent_events: { event_type: string; participant_id: string; campaign_id: string; timestamp: string }[];
}

export interface Campaign {
  id: string;
  name: string;
  description: string;
  status: string;
  training_url?: string;
  created_at: string;
  expires_at: string;
  participant_count?: number;
}

export interface TrainingEvent {
  id: string;
  participant_id: string;
  campaign_id: string;
  event_type: string;
  details: string;
  timestamp: string;
}

export interface LocationEvent {
  id: string;
  participant_id: string;
  campaign_id: string;
  latitude: number | null;
  longitude: number | null;
  permission_status: string;
  timestamp: string;
}

export interface BrowserInfoEntry {
  id: string;
  participant_id: string;
  browser: string;
  os: string;
  screen_resolution: string;
  language: string;
  timezone: string;
  user_agent: string;
  timestamp: string;
}
