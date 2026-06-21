const API_BASE = "http://127.0.0.1:8000";

export async function uploadDocument(file, onProgress) {
  const formData = new FormData();
  formData.append("file", file);
  onProgress?.(35);

  const response = await fetch(`${API_BASE}/upload`, {
    method: "POST",
    body: formData,
  });
  onProgress?.(85);

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || "Upload failed");
  }

  const data = await response.json();
  localStorage.setItem("latestExtraction", JSON.stringify(data));
  onProgress?.(100);
  return data;
}

export async function getDashboard() {
  const response = await fetch(`${API_BASE}/dashboard`);
  if (!response.ok) {
    throw new Error("Dashboard load failed");
  }
  return response.json();
}

export function downloadExcel() {
  window.location.href = `${API_BASE}/download-excel`;
}

export function getLatestExtraction() {
  return JSON.parse(localStorage.getItem("latestExtraction") || "null");
}
