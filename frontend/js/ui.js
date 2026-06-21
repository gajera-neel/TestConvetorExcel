export function markActiveNav() {
  const page = document.body.dataset.page;
  document.querySelectorAll("[data-nav]").forEach((link) => {
    link.classList.toggle("active", link.dataset.nav === page);
  });
}

export function setText(id, value) {
  const element = document.getElementById(id);
  if (element) element.textContent = value || "-";
}

export function renderMetrics(metrics) {
  setText("totalUploads", metrics.total_uploads);
  setText("totalBills", metrics.total_bills);
  setText("totalAmount", metrics.total_amount);
  setText("uniqueVendors", metrics.unique_vendors);
  setText("todaysUploads", metrics.todays_uploads);
}

export function renderBars(containerId, items, labelKey, valueKey) {
  const container = document.getElementById(containerId);
  if (!container) return;
  container.innerHTML = "";
  const max = Math.max(...items.map((item) => Number(item[valueKey]) || 0), 1);

  items.forEach((item) => {
    const row = document.createElement("div");
    row.className = "bar-row";
    row.innerHTML = `
      <span>${item[labelKey]}</span>
      <div><i style="width:${((Number(item[valueKey]) || 0) / max) * 100}%"></i></div>
      <strong>${item[valueKey]}</strong>
    `;
    container.appendChild(row);
  });
}

export function renderRecentUploads(records) {
  const list = document.getElementById("recentUploads");
  if (!list) return;
  list.innerHTML = records.length ? "" : "<li>No uploads yet.</li>";

  records.forEach((record) => {
    const item = document.createElement("li");
    item.innerHTML = `
      <span>${record.filename}</span>
      <strong>${record.detected_type}</strong>
      <small>${record.uploaded_at}</small>
    `;
    list.appendChild(item);
  });
}

export function renderEditableTable(columns, rows) {
  const head = document.getElementById("rawHead");
  const body = document.getElementById("rawBody");
  if (!head || !body) return;

  const visibleColumns = columns.length ? columns : ["Column"];
  const visibleRows = rows.length ? rows : [{}];

  head.innerHTML = `<tr>${visibleColumns.map((column) => `<th data-sort="${column}">${column}</th>`).join("")}<th>Action</th></tr>`;
  body.innerHTML = "";

  visibleRows.forEach((row) => addTableRow(visibleColumns, row));
}

export function addTableRow(columns, row = {}) {
  const body = document.getElementById("rawBody");
  if (!body) return;

  const tr = document.createElement("tr");
  columns.forEach((column) => {
    const td = document.createElement("td");
    td.contentEditable = "true";
    td.textContent = row[column] || "";
    tr.appendChild(td);
  });

  const action = document.createElement("td");
  const button = document.createElement("button");
  button.className = "mini-btn danger";
  button.textContent = "Delete";
  button.addEventListener("click", () => tr.remove());
  action.appendChild(button);
  tr.appendChild(action);
  body.appendChild(tr);
}

export function setupTableTools() {
  const search = document.getElementById("tableSearch");
  const addRow = document.getElementById("addRowBtn");
  const body = document.getElementById("rawBody");
  const head = document.getElementById("rawHead");

  search?.addEventListener("input", () => {
    const query = search.value.toLowerCase();
    body?.querySelectorAll("tr").forEach((row) => {
      row.classList.toggle("hidden", !row.textContent.toLowerCase().includes(query));
    });
  });

  addRow?.addEventListener("click", () => {
    const columns = [...(head?.querySelectorAll("th[data-sort]") || [])].map((th) => th.dataset.sort);
    addTableRow(columns);
  });

  head?.addEventListener("click", (event) => {
    const target = event.target.closest("th[data-sort]");
    if (!target || !body) return;
    const index = [...target.parentElement.children].indexOf(target);
    const rows = [...body.querySelectorAll("tr")].sort((a, b) =>
      a.children[index].textContent.localeCompare(b.children[index].textContent, undefined, { numeric: true }),
    );
    rows.forEach((row) => body.appendChild(row));
  });
}
