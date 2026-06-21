const API_BASE = "http://127.0.0.1:8000";
const API_URL = `${API_BASE}/upload`;
const EXPORT_URL = `${API_BASE}/export`;

const dropZone = document.getElementById("dropZone");
const fileInput = document.getElementById("fileInput");
const uploadBtn = document.getElementById("uploadBtn");
const exportBtn = document.getElementById("exportBtn");
const fileName = document.getElementById("fileName");
const spinner = document.getElementById("spinner");
const successMessage = document.getElementById("successMessage");
const extractedText = document.getElementById("extractedText");
const dashboard = document.getElementById("dashboard");
const structuredSection = document.getElementById("structuredSection");
const lineItemsSection = document.getElementById("lineItemsSection");
const fieldGrid = document.getElementById("fieldGrid");
const lineItemsBody = document.getElementById("lineItemsBody");
const vendorValue = document.getElementById("vendorValue");
const invoiceValue = document.getElementById("invoiceValue");
const dateValue = document.getElementById("dateValue");
const totalValue = document.getElementById("totalValue");

let selectedFile = null;
let latestResult = null;

const FIELD_LABELS = [
  ["vendor", "Vendor"],
  ["invoice_number", "Invoice Number"],
  ["date", "Date"],
  ["currency", "Currency"],
  ["subtotal", "Subtotal"],
  ["tax", "Tax / GST"],
  ["total", "Total"],
];

function valueOrDash(value) {
  return value || "-";
}

function setLoading(isLoading) {
  spinner.classList.toggle("hidden", !isLoading);
  uploadBtn.disabled = isLoading;
  exportBtn.disabled = isLoading || !latestResult;
}

function showSuccess(message) {
  successMessage.textContent = message;
  successMessage.classList.remove("hidden");
}

function clearSuccess() {
  successMessage.textContent = "";
  successMessage.classList.add("hidden");
}

function resetResults() {
  latestResult = null;
  extractedText.value = "";
  fieldGrid.innerHTML = "";
  lineItemsBody.innerHTML = "";
  dashboard.classList.add("hidden");
  structuredSection.classList.add("hidden");
  lineItemsSection.classList.add("hidden");
  exportBtn.classList.add("hidden");
}

function handleFile(file) {
  if (!file) return;
  selectedFile = file;
  fileName.textContent = `Selected: ${file.name}`;
  clearSuccess();
  resetResults();
}

function renderFields(billData) {
  fieldGrid.innerHTML = "";

  FIELD_LABELS.forEach(([key, label]) => {
    const item = document.createElement("div");
    item.className = "field-item";
    const labelEl = document.createElement("span");
    const valueEl = document.createElement("strong");
    labelEl.textContent = label;
    valueEl.textContent = valueOrDash(billData[key]);
    item.append(labelEl, valueEl);
    fieldGrid.appendChild(item);
  });
}

function renderLineItems(items) {
  lineItemsBody.innerHTML = "";

  if (!items.length) {
    const row = document.createElement("tr");
    const cell = document.createElement("td");
    cell.colSpan = 4;
    cell.className = "empty-cell";
    cell.textContent = "No line items detected. Check raw OCR text below.";
    row.appendChild(cell);
    lineItemsBody.appendChild(row);
    return;
  }

  items.forEach((item) => {
    const row = document.createElement("tr");
    ["description", "quantity", "unit_price", "total"].forEach((key) => {
      const cell = document.createElement("td");
      cell.textContent = valueOrDash(item[key]);
      row.appendChild(cell);
    });
    lineItemsBody.appendChild(row);
  });
}

function renderResult(data) {
  latestResult = data;
  const billData = data.bill_data || {};
  const lineItems = billData.line_items || [];

  extractedText.value = data.extracted_text || "";
  vendorValue.textContent = valueOrDash(billData.vendor);
  invoiceValue.textContent = valueOrDash(billData.invoice_number);
  dateValue.textContent = valueOrDash(billData.date);
  totalValue.textContent = valueOrDash(billData.total);

  renderFields(billData);
  renderLineItems(lineItems);

  dashboard.classList.remove("hidden");
  structuredSection.classList.remove("hidden");
  lineItemsSection.classList.remove("hidden");
  exportBtn.classList.remove("hidden");
}

async function uploadFile(file) {
  if (!file) {
    alert("Please select a file first.");
    return;
  }

  const formData = new FormData();
  formData.append("file", file);

  setLoading(true);
  clearSuccess();

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || "Upload failed");
    }

    const data = await response.json();
    console.log(data);

    renderResult(data);
    showSuccess(`Upload successful: ${data.filename}`);
  } catch (error) {
    console.error(error);
    alert(error.message || "Upload failed");
  } finally {
    setLoading(false);
  }
}

async function downloadExcel() {
  if (!latestResult) return;

  setLoading(true);

  try {
    const response = await fetch(EXPORT_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(latestResult),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || "Excel export failed");
    }

    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    const baseName = (latestResult.filename || "bill").replace(/\.[^.]+$/, "");
    link.href = url;
    link.download = `${baseName}_extraction.xlsx`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  } catch (error) {
    console.error(error);
    alert(error.message || "Excel export failed");
  } finally {
    setLoading(false);
  }
}

uploadBtn.addEventListener("click", () => {
  if (selectedFile) {
    uploadFile(selectedFile);
  } else {
    fileInput.click();
  }
});

fileInput.addEventListener("change", (event) => {
  const file = event.target.files[0];
  handleFile(file);
  if (file) {
    uploadFile(file);
  }
});

dropZone.addEventListener("dragover", (event) => {
  event.preventDefault();
  dropZone.classList.add("dragover");
});

dropZone.addEventListener("dragleave", () => {
  dropZone.classList.remove("dragover");
});

dropZone.addEventListener("drop", (event) => {
  event.preventDefault();
  dropZone.classList.remove("dragover");

  const file = event.dataTransfer.files[0];
  handleFile(file);
  if (file) {
    uploadFile(file);
  }
});

exportBtn.addEventListener("click", downloadExcel);
