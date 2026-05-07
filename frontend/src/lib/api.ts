import type { DailyDigestOut, PaperOut, SearchOut, TimelineDay, StatsOut } from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

async function fetchJSON<T>(url: string): Promise<T> {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export async function getLatest(source = '', page = 1): Promise<SearchOut> {
  const params = new URLSearchParams({ page: String(page), size: '30' });
  if (source) params.set('source', source);
  return fetchJSON(`${API_BASE}/latest?${params}`);
}

export async function getFeed(source = '', page = 1): Promise<SearchOut> {
  const params = new URLSearchParams({ page: String(page), size: '30', days: '30' });
  if (source) params.set('source', source);
  return fetchJSON(`${API_BASE}/feed?${params}`);
}

export async function getFeatured(page = 1): Promise<SearchOut> {
  return fetchJSON(`${API_BASE}/featured?page=${page}&size=20&days=60`);
}

export async function getDailyDigest(date: string): Promise<DailyDigestOut> {
  return fetchJSON(`${API_BASE}/papers/daily/${date}`);
}

export async function getTodayDigest(): Promise<DailyDigestOut> {
  return fetchJSON(`${API_BASE}/papers/daily/today`);
}

export async function getPaper(id: string): Promise<PaperOut> {
  return fetchJSON(`${API_BASE}/papers/${id}`);
}

export async function getTimeline(days = 60): Promise<TimelineDay[]> {
  return fetchJSON(`${API_BASE}/timeline?days=${days}`);
}

export async function getStats(): Promise<StatsOut> {
  return fetchJSON(`${API_BASE}/stats`);
}

export async function searchPapers(q: string, source = '', page = 1): Promise<SearchOut> {
  const params = new URLSearchParams({ q, page: String(page), size: '20' });
  if (source) params.set('source', source);
  return fetchJSON(`${API_BASE}/search?${params}`);
}
