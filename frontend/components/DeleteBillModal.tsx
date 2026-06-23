"use client";

import type { UploadedBill } from "@/lib/types";

export function DeleteBillModal({
  bill,
  deleting,
  error,
  onCancel,
  onConfirm,
}: {
  bill: UploadedBill | null;
  deleting: boolean;
  error?: string;
  onCancel: () => void;
  onConfirm: () => void;
}) {
  if (!bill) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/40 p-4 backdrop-blur-sm">
      <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl">
        <h3 className="text-lg font-bold text-slate-950">Delete bill?</h3>
        <p className="mt-2 text-sm text-slate-600">
          This will permanently remove <strong>{bill.filename}</strong> from Supabase and refresh dashboard metrics.
        </p>

        {error ? <div className="mt-4 rounded-lg bg-red-50 p-3 text-sm text-red-700">{error}</div> : null}

        <div className="mt-6 flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
          <button
            type="button"
            onClick={onCancel}
            disabled={deleting}
            className="rounded-lg border border-slate-300 px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50 disabled:opacity-60"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={onConfirm}
            disabled={deleting}
            className="rounded-lg bg-red-600 px-4 py-2 text-sm font-semibold text-white hover:bg-red-700 disabled:opacity-60"
          >
            {deleting ? "Deleting..." : "Delete Bill"}
          </button>
        </div>
      </div>
    </div>
  );
}
