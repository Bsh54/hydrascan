import type { ScanResult } from "./types";

const BASE_URL = import.meta.env.VITE_API_URL ?? "";

async function request<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(`${BASE_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    const detail = await response.json().catch(() => ({}));
    throw new Error(detail.detail ?? `Request failed (${response.status})`);
  }
  return response.json() as Promise<T>;
}

export function scanRepository(repoUrl: string): Promise<ScanResult> {
  return request<ScanResult>("/api/scan", { repoUrl });
}
