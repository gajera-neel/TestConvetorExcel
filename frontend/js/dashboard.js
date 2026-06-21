import { getDashboard } from "./api.js";
import { markActiveNav, renderBars, renderMetrics, renderRecentUploads } from "./ui.js";

markActiveNav();

async function loadDashboard() {
  try {
    const dashboard = await getDashboard();
    renderMetrics(dashboard.metrics);
    renderBars("uploadsByDay", dashboard.uploads_by_day, "day", "count");
    renderBars("amountTrend", dashboard.amount_trend, "day", "amount");
    renderBars("billCategories", dashboard.bill_categories, "detected_type", "count");
    renderRecentUploads(dashboard.recent_uploads);
  } catch (error) {
    alert(error.message || "Dashboard load failed");
  }
}

document.getElementById("refreshBtn").addEventListener("click", loadDashboard);
loadDashboard();
setInterval(loadDashboard, 15000);
