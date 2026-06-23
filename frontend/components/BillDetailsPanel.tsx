"use client";

import { ChartBars } from "@/components/ChartBars";
import { MetricCard } from "@/components/MetricCard";
import { UploadedBillsList } from "@/components/UploadedBillsList";
import type { BillDashboardDetail, DashboardData, UploadedBill } from "@/lib/types";

function displayValue(value?: string | number) {
  return value === undefined || value === null || value === "" ? "Not detected" : value;
}

function RawTable({ bill }: { bill: BillDashboardDetail }) {
  const columns = bill.columns?.length ? bill.columns : Object.keys(bill.rows?.[0] || {});
  const rows = bill.rows || [];

  if (!rows.length || !columns.length) {
    return (
      <div className="rounded-xl border border-dashed border-slate-300 bg-slate-50 p-5 text-sm text-slate-500">
        No raw table rows detected for this bill.
      </div>
    );
  }

  return (
    <div className="max-h-[420px] overflow-auto rounded-xl border border-slate-200 bg-white">
      <table className="w-max min-w-full border-separate border-spacing-0 text-sm">
        <thead className="sticky top-0 z-10 bg-slate-900 text-white">
          <tr>
            {columns.map((column) => (
              <th key={column} className="min-w-[160px] border-b border-slate-700 px-4 py-3 text-left font-semibold">
                {column}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, rowIndex) => (
            <tr key={rowIndex} className="odd:bg-white even:bg-slate-50">
              {columns.map((column) => (
                <td key={`${rowIndex}-${column}`} className="border-b border-slate-100 px-4 py-3 text-slate-700">
                  {displayValue(row[column])}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function BillDetailsPanel({
  dashboard,
  onBack,
  onSelectBill,
  onDeleteBill,
}: {
  dashboard: DashboardData;
  onBack: () => void;
  onSelectBill: (billId: string) => void;
  onDeleteBill: (bill: UploadedBill) => void;
}) {
  const bill = dashboard.bill;

  if (!bill) {
    return (
      <div className="rounded-2xl border border-dashed border-slate-300 bg-slate-50 p-8 text-center text-slate-500">
        Selected bill details are unavailable.
      </div>
    );
  }

  const fieldEntries = Object.entries(bill.fields || {}).filter(([, value]) => String(value || "").trim());

  return (
    <div className="space-y-5">
      <section className="rounded-2xl border border-blue-100 bg-blue-50/70 p-5">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
          <div className="min-w-0">
            <p className="text-sm font-semibold text-blue-700">Viewing: {bill.bill_name || bill.filename}</p>
            <h2 className="mt-1 truncate text-2xl font-bold text-slate-950">{bill.filename}</h2>
            <p className="text-sm text-slate-600">{bill.vendor || "Vendor not detected"} | {bill.uploaded_at}</p>
          </div>
          <button
            type="button"
            onClick={onBack}
            className="rounded-lg bg-slate-950 px-4 py-2.5 text-sm font-semibold text-white hover:bg-slate-800"
          >
            {"<-"} Back To Overall Dashboard
          </button>
        </div>
      </section>

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard label="Total Amount" value={dashboard.metrics.total_amount || "₹0.00"} detail="Selected bill only" />
        <MetricCard label="Tax" value={dashboard.metrics.total_tax || bill.tax || "₹0.00"} detail="GST/tax detected" />
        <MetricCard label="Table Rows" value={bill.rows_count || bill.rows.length} detail="Extracted raw rows" />
        <MetricCard label="Confidence" value={`${dashboard.metrics.success_rate}%`} detail="OCR/extraction confidence" />
      </section>

      <section className="grid gap-5 xl:grid-cols-3">
        <ChartBars title="Amount Breakdown" data={dashboard.amount_breakdown || []} format="currency" />
        <ChartBars title="Generated Charts" data={dashboard.data_volume || []} />
        <ChartBars title="Bill Category" data={dashboard.bill_categories || []} />
      </section>

      <section className="grid gap-5 xl:grid-cols-[1fr_1.2fr]">
        <div className="glass-card rounded-2xl p-5">
          <h3 className="mb-4 text-lg font-bold text-slate-950">Summary</h3>
          <div className="grid gap-3">
            {(dashboard.summary || []).map((item) => (
              <div key={item.label} className="flex justify-between gap-4 rounded-xl bg-slate-50 p-3 text-sm">
                <span className="text-slate-500">{item.label}</span>
                <strong className="text-right text-slate-800">{displayValue(item.value)}</strong>
              </div>
            ))}
          </div>
        </div>

        <div className="glass-card rounded-2xl p-5">
          <h3 className="mb-4 text-lg font-bold text-slate-950">Extracted Fields</h3>
          {fieldEntries.length ? (
            <div className="grid max-h-[360px] gap-3 overflow-y-auto pr-1 sm:grid-cols-2">
              {fieldEntries.map(([key, value]) => (
                <div key={key} className="rounded-xl border border-slate-200 bg-white p-3">
                  <span className="block text-xs font-semibold uppercase tracking-wide text-slate-400">{key}</span>
                  <strong className="mt-1 block break-words text-sm text-slate-800">{value}</strong>
                </div>
              ))}
            </div>
          ) : (
            <div className="rounded-xl border border-dashed border-slate-300 bg-slate-50 p-5 text-sm text-slate-500">
              No field values detected.
            </div>
          )}
        </div>
      </section>

      <section className="glass-card rounded-2xl p-5">
        <h3 className="mb-4 text-lg font-bold text-slate-950">Raw Extraction Preview</h3>
        <RawTable bill={bill} />
        {bill.extracted_text ? (
          <pre className="mt-4 max-h-56 overflow-auto rounded-xl bg-slate-950 p-4 text-xs leading-5 text-slate-100">
            {bill.extracted_text}
          </pre>
        ) : null}
      </section>

      <UploadedBillsList
        bills={dashboard.uploaded_bills || []}
        selectedBillId={bill.id}
        onSelect={onSelectBill}
        onDelete={onDeleteBill}
      />
    </div>
  );
}
