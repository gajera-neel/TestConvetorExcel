import type { DashboardData, UploadResult } from "./types";

export const API_BASE = "http://127.0.0.1:8000";
export const LATEST_KEY = "doc_excel_latest_extraction";

export async function uploadFile(file: File, onProgress?: (value: number) => void): Promise<UploadResult> {
  const formData = new FormData();
  formData.append("file", file);
  onProgress?.(28);

  const response = await fetch(`${API_BASE}/upload`, {
    method: "POST",
    body: formData,
  });
  onProgress?.(86);

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || "Upload failed");
  }

  const data = (await response.json()) as UploadResult;
  localStorage.setItem(LATEST_KEY, JSON.stringify(data));
  onProgress?.(100);
  return data;
}

export async function getDashboard(): Promise<DashboardData> {
  const response = await fetch(`${API_BASE}/dashboard`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error("Dashboard load failed");
  }
  return response.json();
}

export async function generateExcel(rows: Record<string, string>[], columns: string[], sessionId?: string): Promise<Blob> {
  const response = await fetch(`${API_BASE}/generate-excel`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ rows, columns, session_id: sessionId }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || "Excel generation failed");
  }

  return response.blob();
}

export function loadLatestExtraction(): UploadResult | null {
  if (typeof window === "undefined") return null;
  const raw = localStorage.getItem(LATEST_KEY);
  return raw ? (JSON.parse(raw) as UploadResult) : null;
}
