import { downloadExcel, getLatestExtraction } from "./api.js";
import { markActiveNav, renderEditableTable } from "./ui.js";

markActiveNav();

const latest = getLatestExtraction();
if (latest?.extracted_fields) {
  renderEditableTable(latest.extracted_fields.columns || [], latest.extracted_fields.rows || []);
} else {
  renderEditableTable(["Message"], [{ Message: "No extraction found. Upload a file first." }]);
}

document.getElementById("downloadBtn").addEventListener("click", downloadExcel);
