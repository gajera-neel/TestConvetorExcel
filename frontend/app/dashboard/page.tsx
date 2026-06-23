"use client";

import { Suspense, useCallback, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { AppShell } from "@/components/AppShell";
import { BillDetailsPanel } from "@/components/BillDetailsPanel";
import { DashboardOverview } from "@/components/DashboardOverview";
import { DeleteBillModal } from "@/components/DeleteBillModal";
import { Skeleton } from "@/components/Skeleton";
import { deleteBill, getDashboard } from "@/lib/api";
import type { DashboardData, UploadedBill } from "@/lib/types";

function DashboardContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const selectedBillId = searchParams.get("bill") || searchParams.get("bill_id");
  const [dashboard, setDashboard] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [pendingDelete, setPendingDelete] = useState<UploadedBill | null>(null);
  const [deleting, setDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState("");

  const loadDashboard = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      setDashboard(await getDashboard(selectedBillId));
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "Dashboard load failed");
    } finally {
      setLoading(false);
    }
  }, [selectedBillId]);

  useEffect(() => {
    loadDashboard();
    const timer = setInterval(loadDashboard, 15000);
    return () => clearInterval(timer);
  }, [loadDashboard]);

  useEffect(() => {
    if (!dashboard?.calculation_issues?.length) return;
    dashboard.calculation_issues.forEach((issue) => {
      console.groupCollapsed(`[DocExcel] Calculation review needed: ${issue.filename || issue.id || "Bill"}`);
      console.warn("Issues", issue.audit.issues);
      console.info("Sources", issue.audit.sources);
      console.info("Totals", {
        subtotal: issue.audit.subtotal,
        tax: issue.audit.tax,
        discount: issue.audit.discount,
        total: issue.audit.total,
        expectedTotal: issue.audit.expected_total,
        difference: issue.audit.difference,
      });
      console.info("Raw fields", issue.audit.raw_fields);
      console.info("Raw rows", issue.audit.raw_rows);
      console.groupEnd();
    });
  }, [dashboard]);

  function selectBill(billId: string) {
    router.push(`/dashboard?bill=${encodeURIComponent(billId)}`);
  }

  function backToOverall() {
    router.push("/dashboard");
  }

  async function confirmDelete() {
    if (!pendingDelete) return;
    setDeleting(true);
    setDeleteError("");
    try {
      const refreshed = await deleteBill(pendingDelete.id);
      setPendingDelete(null);
      setDashboard(refreshed);
      if (selectedBillId === pendingDelete.id) {
        router.push("/dashboard");
      } else {
        await loadDashboard();
      }
    } catch (deleteFailure) {
      setDeleteError(deleteFailure instanceof Error ? deleteFailure.message : "Delete failed");
    } finally {
      setDeleting(false);
    }
  }

  return (
    <AppShell>
      <div className="space-y-4 pr-0 sm:space-y-5 lg:max-h-[calc(100vh-2rem)] lg:overflow-y-auto lg:pr-1">
        <header className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="text-xl font-semibold text-slate-950">
              {selectedBillId ? `Viewing: ${dashboard?.bill?.bill_name || dashboard?.bill?.filename || "Selected Bill"}` : "Overall Dashboard"}
            </h2>
            <p className="text-sm text-slate-500">
              {selectedBillId ? "Single bill analytics from Supabase." : "Global analytics across all uploaded bills in Supabase."}
            </p>
          </div>
          <button
            onClick={loadDashboard}
            disabled={loading}
            className="w-full rounded-lg border border-slate-300 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 disabled:opacity-60 sm:w-auto"
          >
            Refresh
          </button>
        </header>

        {error ? (
          <div className="rounded-2xl border border-red-200 bg-red-50 p-5 text-sm text-red-700">
            {error}
          </div>
        ) : null}

        {loading && !dashboard ? (
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <Skeleton className="h-36" />
            <Skeleton className="h-36" />
            <Skeleton className="h-36" />
            <Skeleton className="h-36" />
          </div>
        ) : dashboard && selectedBillId ? (
          <BillDetailsPanel
            dashboard={dashboard}
            onBack={backToOverall}
            onSelectBill={selectBill}
            onDeleteBill={setPendingDelete}
          />
        ) : dashboard ? (
          <DashboardOverview
            dashboard={dashboard}
            onSelectBill={selectBill}
            onDeleteBill={setPendingDelete}
          />
        ) : (
          <div className="rounded-2xl border border-dashed border-slate-300 bg-slate-50 p-8 text-center text-sm text-slate-500">
            Dashboard is empty. Upload a bill to start analytics.
          </div>
        )}
      </div>
      <DeleteBillModal
        bill={pendingDelete}
        deleting={deleting}
        error={deleteError}
        onCancel={() => setPendingDelete(null)}
        onConfirm={confirmDelete}
      />
    </AppShell>
  );
}

export default function DashboardPage() {
  return (
    <Suspense fallback={<Skeleton className="h-36" />}>
      <DashboardContent />
    </Suspense>
  );
}
