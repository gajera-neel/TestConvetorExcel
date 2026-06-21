"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/AppShell";
import { ChartBars } from "@/components/ChartBars";
import { GlassPanel } from "@/components/GlassPanel";
import { MetricCard } from "@/components/MetricCard";
import { Skeleton } from "@/components/Skeleton";
import { getDashboard } from "@/lib/api";
import type { DashboardData } from "@/lib/types";

export default function DashboardPage() {
  const [dashboard, setDashboard] = useState<DashboardData | null>(null);

  async function loadDashboard() {
    setDashboard(await getDashboard());
  }

  useEffect(() => {
    loadDashboard();
    const timer = setInterval(loadDashboard, 15000);
    return () => clearInterval(timer);
  }, []);

  return (
    <AppShell>
      <div className="space-y-4 sm:space-y-5">
        <header className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="text-xl font-semibold text-slate-950">Dashboard</h2>
            <p className="text-sm text-slate-500">Live extraction activity and uploaded document metrics.</p>
          </div>
          <button onClick={loadDashboard} className="rounded-lg border border-slate-300 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50">
            Refresh
          </button>
        </header>

        {dashboard ? (
          <>
            <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
              <MetricCard label="Total Bill Value" value={dashboard.metrics.total_amount || "₹0.00"} detail="Sum of detected bill amounts" />
              <MetricCard label="Average Bill" value={dashboard.metrics.average_bill_amount || "₹0.00"} detail="Average processed amount" />
              <MetricCard label="Bills Processed" value={dashboard.metrics.bills} detail={`${dashboard.metrics.uploads} total uploads`} />
              <MetricCard label="Success Rate" value={`${dashboard.metrics.success_rate}%`} detail="OCR confidence average" />
            </section>

            <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
              <MetricCard label="Extracted Rows" value={dashboard.metrics.total_records} detail="Line items and table rows" />
              <MetricCard label="Unique Vendors" value={dashboard.metrics.unique_vendors || 0} detail="Detected vendors/shops" />
              <MetricCard label="Highest Bill" value={dashboard.metrics.highest_bill_amount || "₹0.00"} detail="Largest bill amount" />
              <MetricCard label="Today Uploads" value={dashboard.metrics.todays_uploads || 0} detail="Files uploaded today" />
            </section>

            <section className="grid gap-5 xl:grid-cols-3">
              <ChartBars title="Amount Trend" data={dashboard.amount_trend || []} format="currency" />
              <ChartBars title="Bill Categories" data={dashboard.bill_categories || []} />
              <ChartBars title="Top Vendors" data={dashboard.top_vendors || []} format="currency" />
            </section>

            <section className="grid gap-5 xl:grid-cols-3">
              <ChartBars title="Extraction Activity" data={dashboard.extraction_activity || []} />
              <ChartBars title="File Types" data={dashboard.file_types || []} />
              <ChartBars title="Data Volume" data={dashboard.data_volume || []} />
            </section>

            <GlassPanel>
              <div className="mb-5 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                <h3 className="text-xl font-bold">Recent Documents</h3>
                <span className="text-sm text-slate-400">Auto updates</span>
              </div>
              <div className="grid gap-3">
                {dashboard.recent_uploads.length ? (
                  dashboard.recent_uploads.map((file) => (
                    <div key={`${file.filename}-${file.uploaded_at}`} className="grid gap-3 rounded-xl border border-slate-200 bg-slate-50 p-4 transition hover:border-blue-200 hover:bg-white lg:grid-cols-[1.4fr_1fr_120px_110px_170px] lg:items-center">
                      <div className="min-w-0">
                        <strong className="block truncate text-slate-900">{file.filename}</strong>
                        <span className="text-xs text-slate-500">{file.vendor || "Vendor not detected"}</span>
                      </div>
                      <span className="rounded-full bg-blue-50 px-3 py-1 text-center text-sm text-blue-700">{file.detected_type}</span>
                      <strong className="text-sm text-slate-900">{file.amount || "₹0.00"}</strong>
                      <span className="text-sm text-slate-600">{file.rows_count || 0} rows</span>
                      <small className="text-slate-500">{file.uploaded_at}</small>
                    </div>
                  ))
                ) : (
                  <div className="rounded-xl border border-dashed border-slate-300 bg-slate-50 p-6 text-center text-sm text-slate-500">
                    No documents uploaded yet. Upload a file to build dashboard data.
                  </div>
                )}
              </div>
            </GlassPanel>
          </>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <Skeleton className="h-36" />
            <Skeleton className="h-36" />
            <Skeleton className="h-36" />
            <Skeleton className="h-36" />
          </div>
        )}
      </div>
    </AppShell>
  );
}
