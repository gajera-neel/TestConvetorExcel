import { uploadDocument } from "./api.js";
import { markActiveNav, renderEditableTable, setText, setupTableTools } from "./ui.js";

markActiveNav();
setupTableTools();

const dropZone = document.getElementById("dropZone");
const fileInput = document.getElementById("fileInput");
const uploadBtn = document.getElementById("uploadBtn");
const preview = document.getElementById("preview");
const previewImage = document.getElementById("previewImage");
const fileName = document.getElementById("fileName");
const fileMeta = document.getElementById("fileMeta");
const progressBar = document.getElementById("progressBar");
const resultSection = document.getElementById("resultSection");
const textSection = document.getElementById("textSection");
const logsSection = document.getElementById("logsSection");
const extractedText = document.getElementById("extractedText");
const logs = document.getElementById("logs");

function setProgress(value) {
  progressBar.style.width = `${value}%`;
}

function showPreview(file) {
  preview.classList.remove("hidden");
  fileName.textContent = file.name;
  fileMeta.textContent = `${file.type || "Unknown type"} • ${(file.size / 1024).toFixed(1)} KB`;
  setProgress(10);

  if (file.type.startsWith("image/")) {
    previewImage.src = URL.createObjectURL(file);
    previewImage.classList.remove("hidden");
  } else {
    previewImage.classList.add("hidden");
  }
}

function renderLogs(items) {
  logs.innerHTML = "";
  items.forEach((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    logs.appendChild(li);
  });
}

function renderResult(data) {
  const extracted = data.extracted_fields || { columns: [], rows: [] };
  setText("confidenceScore", `${Math.round((data.confidence || 0) * 100)}%`);
  setText("detectedType", data.detected_type);
  extractedText.value = data.extracted_text || "";
  renderEditableTable(extracted.columns || [], extracted.rows || []);
  renderLogs(data.logs || []);
  resultSection.classList.remove("hidden");
  textSection.classList.remove("hidden");
  logsSection.classList.remove("hidden");
}

async function analyzeFile(file) {
  if (!file) return;
  showPreview(file);
  uploadBtn.disabled = true;

  try {
    const data = await uploadDocument(file, setProgress);
    renderResult(data);
  } catch (error) {
    alert(error.message || "Upload failed");
    setProgress(0);
  } finally {
    uploadBtn.disabled = false;
  }
}

uploadBtn.addEventListener("click", () => fileInput.click());
fileInput.addEventListener("change", (event) => analyzeFile(event.target.files[0]));

dropZone.addEventListener("dragover", (event) => {
  event.preventDefault();
  dropZone.classList.add("dragover");
});

dropZone.addEventListener("dragleave", () => dropZone.classList.remove("dragover"));

dropZone.addEventListener("drop", (event) => {
  event.preventDefault();
  dropZone.classList.remove("dragover");
  analyzeFile(event.dataTransfer.files[0]);
});
