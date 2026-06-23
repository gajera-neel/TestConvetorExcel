"use client";

import { ChartBars } from "@/components/ChartBars";
import { MetricCard } from "@/components/MetricCard";
import { UploadedBillsList } from "@/components/UploadedBillsList";
import type { DashboardData, UploadedBill } from "@/lib/types";

export function DashboardOverview({
  dashboard,
  onSelectBill,
  onDeleteBill,
}: {
  dashboard: DashboardData;
  onSelectBill: (billId: string) => void;
  onDeleteBill: (bill: UploadedBill) => void;
}) {
  return (
    <div className="space-y-5">
      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard label="Total Bills" value={dashboard.metrics.total_bills ?? dashboard.metrics.bills} detail="Bill, invoice, and receipt records" />
        <MetricCard label="Total Amount" value={dashboard.metrics.total_amount || "₹0.00"} detail="All uploaded bills combined" />
        <MetricCard label="Total Tax" value={dashboard.metrics.total_tax || "₹0.00"} detail="GST/tax detected across bills" />
        <MetricCard label="Average Bill" value={dashboard.metrics.average_bill_amount || "₹0.00"} detail="Average bill amount" />
      </section>

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard label="Total Upload Count" value={dashboard.metrics.total_uploads ?? dashboard.metrics.uploads} detail="Stored in Supabase" />
        <MetricCard label="Extracted Rows" value={dashboard.metrics.total_records} detail="Line items and raw rows" />
        <MetricCard label="Unique Vendors" value={dashboard.metrics.unique_vendors || 0} detail="Detected vendors/shops" />
        <MetricCard label="Success Rate" value={`${dashboard.metrics.success_rate}%`} detail="Average extraction confidence" />
      </section>

      <section className="grid gap-5 xl:grid-cols-3">
        <ChartBars title="Amount Trend" data={dashboard.amount_trend || []} format="currency" />
        <ChartBars title="Top Vendors" data={dashboard.top_vendors || []} format="currency" />
        <ChartBars title="Bill Categories" data={dashboard.bill_categories || []} />
      </section>

      <section className="grid gap-5 xl:grid-cols-3">
        <ChartBars title="Extraction Activity" data={dashboard.extraction_activity || []} />
        <ChartBars title="File Types" data={dashboard.file_types || []} />
        <ChartBars title="Data Volume" data={dashboard.data_volume || []} />
      </section>

      <UploadedBillsList
        bills={dashboard.uploaded_bills || []}
        onSelect={onSelectBill}
        onDelete={onDeleteBill}
      />
    </div>
  );
}
