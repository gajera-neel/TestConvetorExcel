"use client";

import { motion } from "framer-motion";
import type { UploadedBill } from "@/lib/types";

function formatDate(value: string) {
  if (!value) return "Unknown date";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString();
}

export function UploadedBillsList({
  bills,
  selectedBillId,
  onSelect,
  onDelete,
}: {
  bills: UploadedBill[];
  selectedBillId?: string | null;
  onSelect: (billId: string) => void;
  onDelete: (bill: UploadedBill) => void;
}) {
  return (
    <section className="glass-card rounded-2xl p-4 sm:p-5">
      <div className="mb-4 flex items-center justify-between gap-3">
        <div>
          <h3 className="text-lg font-bold text-slate-950">Uploaded Bills</h3>
          <p className="text-sm text-slate-500">Click any bill to view document-level analytics.</p>
        </div>
        <span className="rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700">{bills.length} files</span>
      </div>

      {bills.length ? (
        <div className="max-h-[560px] space-y-3 overflow-y-auto pr-1">
          {bills.map((bill) => {
            const isSelected = selectedBillId === bill.id;
            return (
              <motion.article
                key={bill.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className={`rounded-2xl border bg-white p-4 shadow-sm transition ${
                  isSelected ? "border-blue-300 ring-2 ring-blue-100" : "border-slate-200 hover:border-blue-200"
                }`}
              >
                <div className="grid gap-3 lg:grid-cols-[1.4fr_1fr_110px_110px_160px] lg:items-center">
                  <button type="button" onClick={() => onSelect(bill.id)} className="min-w-0 text-left">
                    <strong className="block truncate text-sm font-bold text-slate-950">{bill.filename}</strong>
                    <span className="block truncate text-xs text-slate-500">{formatDate(bill.uploaded_at)}</span>
                  </button>
                  <div className="min-w-0">
                    <span className="block truncate text-sm font-semibold text-slate-700">{bill.vendor || "Vendor not detected"}</span>
                    <span className="text-xs text-slate-500">{bill.file_type || bill.detected_type || "document"}</span>
                  </div>
                  <strong className="text-sm text-slate-950">{bill.amount || "₹0.00"}</strong>
                  <span className="rounded-full bg-emerald-50 px-3 py-1 text-center text-xs font-semibold text-emerald-700">
                    {bill.status || "processed"}
                  </span>
                  <div className="flex gap-2 lg:justify-end">
                    <button
                      type="button"
                      onClick={() => onSelect(bill.id)}
                      className="rounded-lg border border-slate-200 px-3 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-50"
                    >
                      Preview
                    </button>
                    <button
                      type="button"
                      onClick={() => onDelete(bill)}
                      className="rounded-lg border border-red-200 px-3 py-2 text-xs font-semibold text-red-600 hover:bg-red-50"
                    >
                      Delete
                    </button>
                  </div>
                </div>
              </motion.article>
            );
          })}
        </div>
      ) : (
        <div className="rounded-xl border border-dashed border-slate-300 bg-slate-50 p-6 text-center text-sm text-slate-500">
          No uploaded bills yet. Upload a document to build dashboard analytics.
        </div>
      )}
    </section>
  );
}
