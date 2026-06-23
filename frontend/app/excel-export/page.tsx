"use client";

import { useEffect, useState } from "react";
import { AppShell } from "@/components/AppShell";
import { EditableDataTable } from "@/components/EditableDataTable";
import { GlassPanel } from "@/components/GlassPanel";
import { generateExcel, loadLatestExtraction } from "@/lib/api";
import type { UploadResult } from "@/lib/types";

export default function ExcelExportPage() {
  const [latest, setLatest] = useState<UploadResult | null>(null);
  const [columns, setColumns] = useState<string[]>([]);
  const [rows, setRows] = useState<Record<string, string>[]>([]);
  const [status, setStatus] = useState("Ready to generate formatted Excel");

  useEffect(() => {
    const data = loadLatestExtraction();
    setLatest(data);
    setColumns(data?.extracted_fields.columns || ["Message"]);
    setRows(data?.extracted_fields.rows?.length ? data.extracted_fields.rows : data ? [data.extracted_fields.fields] : [{ Message: "Upload a file first to preview export data." }]);
  }, []);

  async function download() {
    try {
      setStatus("Generating export_date.xlsx...");
      const blob = await generateExcel(rows, columns, latest?.id);
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `export_${new Date().toISOString().slice(0, 10).replaceAll("-", "")}.xlsx`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
      setStatus("Download completed");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Export failed");
    }
  }

  return (
    <AppShell>
      <div className="space-y-4 sm:space-y-5">
        <header className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="text-xl font-semibold text-slate-950">Excel Export</h2>
            <p className="text-sm text-slate-500">Generate formatted workbook from edited raw data.</p>
          </div>
          <button onClick={download} className="w-full rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-bold text-white shadow-sm transition hover:bg-blue-700 sm:w-auto">
            Download Excel
          </button>
        </header>

        <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          <GlassPanel>
            <p className="text-sm text-slate-500">Filename</p>
            <strong className="mt-2 block text-xl text-slate-950 sm:text-2xl">export_date.xlsx</strong>
          </GlassPanel>
          <GlassPanel>
            <p className="text-sm text-slate-500">Rows</p>
            <strong className="mt-2 block text-2xl text-slate-950">{rows.length}</strong>
          </GlassPanel>
          <GlassPanel>
            <p className="text-sm text-slate-500">Status</p>
            <strong className="mt-2 block text-lg text-blue-700">{status}</strong>
          </GlassPanel>
        </section>

        <GlassPanel className="min-w-0 overflow-hidden">
          <div className="mb-5 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
            <div>
            <h3 className="text-xl font-bold">Export Preview</h3>
            <p className="text-sm text-slate-500">Edit final rows and columns before generating Excel.</p>
            </div>
            <span className="rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-xs text-blue-700">
              Filters + frozen header enabled
            </span>
          </div>
          <EditableDataTable
            columns={columns}
            rows={rows}
            onChange={(nextColumns, nextRows) => {
              setColumns(nextColumns);
              setRows(nextRows);
            }}
          />
        </GlassPanel>
      </div>
    </AppShell>
  );
}
