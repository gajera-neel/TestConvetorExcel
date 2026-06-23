"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { motion } from "framer-motion";
import { AppShell } from "@/components/AppShell";
import { EditableDataTable } from "@/components/EditableDataTable";
import { GlassPanel } from "@/components/GlassPanel";
import { generateExcel, uploadFile, warmBackend } from "@/lib/api";
import type { UploadResult } from "@/lib/types";

export default function UploadPage() {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);
  const [progress, setProgress] = useState(0);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<UploadResult | null>(null);
  const [columns, setColumns] = useState<string[]>([]);
  const [rows, setRows] = useState<Record<string, string>[]>([]);
  const [previewUrl, setPreviewUrl] = useState("");
  const [previewMime, setPreviewMime] = useState("");
  const [previewZoom, setPreviewZoom] = useState(1);
  const [recent, setRecent] = useState<string[]>([]);

  const confidence = useMemo(() => Math.round((result?.confidence || 0) * 100), [result]);
  const previewIsImage = previewMime.startsWith("image/");

  function cleanObject<T extends Record<string, unknown>>(item: T): Partial<T> {
    return Object.fromEntries(
      Object.entries(item).filter(([, value]) => value !== null && value !== undefined && value !== "")
    ) as Partial<T>;
  }

  function cleanRows(items: Record<string, string>[]) {
    return items.map((item) => cleanObject(item)).filter((item) => Object.keys(item).length > 0);
  }

  function rowsFromExtraction(data: UploadResult) {
    const fallbackFields = cleanObject(data.extracted_fields.fields);
    return data.extracted_fields.rows.length
      ? data.extracted_fields.rows
      : Object.keys(fallbackFields).length
      ? [fallbackFields as Record<string, string>]
      : [];
  }

  function logExtractionDebug(file: File, data: UploadResult) {
    const tableRows = cleanRows(data.extracted_fields.rows.length ? data.extracted_fields.rows : [data.extracted_fields.fields]);
    const fields = cleanObject(data.extracted_fields.fields);
    const summary = cleanObject({
      id: data.id,
      filename: data.filename,
      fileType: data.file_type,
      detectedType: data.detected_type,
      confidence: data.confidence,
      rowCount: tableRows.length,
      columnCount: data.extracted_fields.columns.length,
    });

    console.groupCollapsed(`[DocExcel] Extraction result: ${file.name}`);
    console.info("Summary", summary);
    if (data.extracted_fields.columns.length) console.info("Columns", data.extracted_fields.columns);
    if (tableRows.length) console.table(tableRows);
    if (Object.keys(fields).length) console.info("Fields", fields);
    if (data.extracted_text) console.info("Raw OCR text", data.extracted_text);
    if (data.logs.length) console.info("Extraction logs", data.logs);
    console.info("Full API response", data);
    console.groupEnd();
  }

  useEffect(() => {
    warmBackend();
  }, []);

  async function handleFile(file?: File) {
    if (!file) return;
    setPreviewUrl(URL.createObjectURL(file));
    setPreviewMime(file.type);
    setPreviewZoom(1);
    setLoading(true);
    setProgress(8);
    const progressTimer = window.setInterval(() => {
      setProgress((value) => (value < 82 ? value + 3 : value));
    }, 900);

    try {
      const data = await uploadFile(file, setProgress);
      logExtractionDebug(file, data);
      const nextRows = rowsFromExtraction(data);
      setResult(data);
      setColumns(data.extracted_fields.columns);
      setRows(nextRows);
      setRecent((items) => [file.name, ...items.filter((item) => item !== file.name)].slice(0, 6));
    } catch (error) {
      console.error("[DocExcel] Upload failed", { fileName: file.name, error });
      alert(error instanceof Error ? error.message : "Upload failed");
      setProgress(0);
    } finally {
      window.clearInterval(progressTimer);
      setLoading(false);
    }
  }

  async function downloadEditedExcel() {
    const blob = await generateExcel(rows, columns, result?.id);
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `export_${new Date().toISOString().slice(0, 10).replaceAll("-", "")}.xlsx`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  }

  function updatePreviewZoom(nextZoom: number) {
    setPreviewZoom(Math.min(2.5, Math.max(0.5, Number(nextZoom.toFixed(2)))));
  }

  return (
    <AppShell>
      <div className="space-y-4">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="text-xl font-semibold text-slate-950">Upload</h2>
            <p className="text-sm text-slate-500">Upload bills, invoices, receipts, images, or PDFs.</p>
          </div>
          <button onClick={() => inputRef.current?.click()} className="rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-blue-700">
            + Upload Document
          </button>
        </div>

        <section className="grid gap-3 md:grid-cols-3">
          <div className="rounded-xl border border-slate-200 bg-white p-4">
            <p className="text-xs font-semibold uppercase text-slate-500">Uploaded Files</p>
            <strong className="mt-2 block text-2xl text-slate-950">{recent.length}</strong>
          </div>
          <div className="rounded-xl border border-slate-200 bg-white p-4">
            <p className="text-xs font-semibold uppercase text-slate-500">Extracted Rows</p>
            <strong className="mt-2 block text-2xl text-slate-950">{rows.length}</strong>
          </div>
          <div className="rounded-xl border border-slate-200 bg-white p-4">
            <p className="text-xs font-semibold uppercase text-slate-500">Confidence</p>
            <strong className="mt-2 block text-2xl text-slate-950">{result ? `${confidence}%` : "0%"}</strong>
          </div>
        </section>

        <section className="flex flex-col gap-3 rounded-xl border border-slate-200 bg-white p-3 lg:flex-row lg:items-center lg:justify-between">
          <div className="flex flex-col gap-3 sm:flex-row">
            <input disabled placeholder="Search file name" className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm placeholder:text-slate-400" />
            <select disabled className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-500">
              <option>All file types</option>
            </select>
          </div>
          <div className="flex gap-2">
            <button className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700">Report</button>
            <button onClick={() => inputRef.current?.click()} className="rounded-lg bg-blue-600 px-3 py-2 text-sm font-semibold text-white">Upload</button>
          </div>
        </section>

        <section className="border-b border-slate-200 bg-white">
          <div className="flex gap-6 overflow-auto text-sm">
            {["Upload", "Raw Data", "Reviewed", "Excel Ready"].map((tab, index) => (
              <span key={tab} className={`whitespace-nowrap border-b-2 py-3 ${index === 0 ? "border-slate-950 font-semibold text-slate-950" : "border-transparent text-slate-500"}`}>
                {tab}
              </span>
            ))}
          </div>
        </section>

        <section className="rounded-xl border border-slate-200 bg-white p-4">
          <div
            onDragOver={(event) => {
              event.preventDefault();
              setDragging(true);
            }}
            onDragLeave={() => setDragging(false)}
            onDrop={(event) => {
              event.preventDefault();
              setDragging(false);
              handleFile(event.dataTransfer.files[0]);
            }}
            className={`relative mx-auto grid min-h-[300px] max-w-xl place-items-center overflow-hidden rounded-xl border border-dashed p-5 text-center transition sm:min-h-[340px] sm:p-8 ${
              dragging ? "border-blue-500 bg-blue-50" : "border-slate-300 bg-slate-50"
            }`}
          >
            <div className="relative">
              <div className="mx-auto mb-5 flex h-16 w-16 items-center justify-center rounded-2xl bg-blue-600 text-3xl text-white shadow-sm">
                ⇪
              </div>
              <h3 className="text-2xl font-bold text-slate-950 sm:text-3xl">Drop JPG, PNG, PDF, or scan here</h3>
              <p className="mx-auto mt-2 max-w-xl text-sm leading-6 text-slate-500 sm:text-base">After upload, extracted data will appear below as an editable raw table.</p>
              <div className="mt-6 grid gap-3 sm:flex sm:flex-wrap sm:justify-center">
                <button onClick={() => inputRef.current?.click()} className="rounded-lg bg-blue-600 px-6 py-3 font-semibold text-white shadow-sm hover:bg-blue-700">
                  Upload Button
                </button>
                <button onClick={() => inputRef.current?.click()} className="rounded-lg border border-slate-300 bg-white px-6 py-3 font-semibold text-slate-700 hover:bg-slate-50">
                  Camera Scan
                </button>
              </div>
              <input ref={inputRef} hidden type="file" accept=".jpg,.jpeg,.png,.pdf" onChange={(event) => handleFile(event.target.files?.[0])} />
            </div>
          </div>

          <div className="mt-5 h-3 overflow-hidden rounded-full bg-slate-100">
            <motion.div animate={{ width: `${progress}%` }} className="h-full rounded-full bg-blue-600" />
          </div>
          {loading ? <p className="mt-3 text-sm text-blue-600">Analyzing file, extracting data, and generating dynamic columns...</p> : null}
        </section>

        {(previewUrl || result) && (
          <div className="grid min-w-0 gap-5 xl:grid-cols-[minmax(320px,420px)_minmax(0,1fr)]">
            <GlassPanel className="min-w-0 overflow-hidden">
              <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <h3 className="text-xl font-bold">Original Preview</h3>
                {previewUrl ? (
                  <div className="flex flex-wrap items-center gap-2">
                    <button
                      onClick={() => updatePreviewZoom(previewZoom - 0.1)}
                      className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50"
                    >
                      -
                    </button>
                    <span className="min-w-[64px] rounded-lg bg-slate-50 px-3 py-2 text-center text-sm font-semibold text-slate-700">
                      {Math.round(previewZoom * 100)}%
                    </span>
                    <button
                      onClick={() => updatePreviewZoom(previewZoom + 0.1)}
                      className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50"
                    >
                      +
                    </button>
                    <button
                      onClick={() => updatePreviewZoom(1)}
                      className="rounded-lg bg-blue-50 px-3 py-2 text-sm font-semibold text-blue-600 hover:bg-blue-100"
                    >
                      Reset
                    </button>
                  </div>
                ) : null}
              </div>
              {previewUrl ? (
                <div className="h-[360px] overflow-auto rounded-3xl border border-white/10 bg-white [scrollbar-color:#94a3b8_#f1f5f9] [scrollbar-width:thin] sm:h-[520px] [&::-webkit-scrollbar]:h-3 [&::-webkit-scrollbar]:w-3 [&::-webkit-scrollbar-thumb]:rounded-full [&::-webkit-scrollbar-thumb]:bg-slate-400 [&::-webkit-scrollbar-track]:bg-slate-100">
                  <div
                    style={{
                      width: `${previewZoom * 100}%`,
                      minWidth: "100%",
                      minHeight: "100%",
                      height: previewIsImage ? "auto" : `${previewZoom * 520}px`,
                    }}
                  >
                    {previewIsImage ? (
                      <img src={previewUrl} alt="Uploaded document preview" className="block h-auto w-full max-w-none bg-white" />
                    ) : (
                      <iframe title="Uploaded document preview" src={previewUrl} className="block h-full w-full bg-white" />
                    )}
                  </div>
                </div>
              ) : (
                <div className="grid h-[360px] place-items-center rounded-3xl bg-white/5 text-slate-400 sm:h-[520px]">No preview</div>
              )}
              <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
                <div className="rounded-xl bg-slate-50 p-4">
                  <p className="text-slate-500">Detected</p>
                  <strong className="text-slate-950">{result?.detected_type || "-"}</strong>
                </div>
                <div className="rounded-xl bg-slate-50 p-4">
                  <p className="text-slate-500">Confidence</p>
                  <strong className="text-slate-950">{confidence}%</strong>
                </div>
              </div>
            </GlassPanel>

            <GlassPanel className="min-w-0 overflow-hidden">
              <div className="mb-5 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
                <div>
                  <h3 className="text-xl font-bold">Extraction Review</h3>
                  <p className="text-sm text-slate-500">Edit, delete, add fields, rename columns, then export.</p>
                </div>
                <button disabled={!rows.length} onClick={downloadEditedExcel} className="rounded-lg bg-blue-600 px-5 py-3 font-semibold text-white shadow-sm hover:bg-blue-700 disabled:opacity-40">
                  Generate Excel
                </button>
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
        )}

        <div className="grid gap-5 lg:grid-cols-2">
          <GlassPanel>
            <h3 className="mb-4 text-xl font-bold">Recent Uploaded Files</h3>
            <div className="grid gap-3">
              {recent.length ? (
                recent.map((file) => (
                  <div key={file} className="flex items-center justify-between rounded-xl border border-slate-200 bg-slate-50 p-4">
                    <span className="text-slate-700">{file}</span>
                    <small className="text-blue-600">Ready</small>
                  </div>
                ))
              ) : (
                <div className="rounded-xl border border-dashed border-slate-300 bg-slate-50 p-4 text-sm text-slate-500">
                  No recent uploads yet. Upload a file to see it here.
                </div>
              )}
            </div>
          </GlassPanel>

          <GlassPanel>
            <h3 className="mb-4 text-xl font-bold">Extraction Logs</h3>
            <ul className="grid gap-2 text-sm text-slate-600">
              {result?.logs?.length ? (
                result.logs.map((log) => (
                  <li key={log} className="rounded-xl bg-slate-50 p-3">
                    {log}
                  </li>
                ))
              ) : (
                <li className="rounded-xl border border-dashed border-slate-300 bg-slate-50 p-3 text-slate-500">
                  Extraction logs will appear after upload.
                </li>
              )}
            </ul>
          </GlassPanel>
        </div>
      </div>
    </AppShell>
  );
}
