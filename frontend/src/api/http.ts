import { QueryClient } from '@tanstack/react-query';
export const queryClient = new QueryClient();
export const customInstance = async <T>(config: { url: string; method: string; params?: any; data?: any; headers?: Record<string,string> }): Promise<T> => {
  const baseURL = import.meta.env.VITE_API_BASE_URL ?? '/api/v1';
  const url = config.url.startsWith("/api/") ? `http://localhost:8000${config.url}${config.params ? `?${new URLSearchParams(config.params)}` : ""}` : baseURL + config.url + (config.params ? `?${new URLSearchParams(config.params)}` : "");
  const res = await fetch(url, { method: config.method, headers: { 'Content-Type': 'application/json', ...(config.headers??{}) }, body: config.data ? JSON.stringify(config.data) : undefined, credentials: 'include' });
  if (!res.ok) throw new Error(`HTTP ${res.status} - ${await res.text()}`);
  return res.json() as Promise<T>;
};
