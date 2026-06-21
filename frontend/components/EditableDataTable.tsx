"use client";

import { useMemo, useRef, useState, type WheelEvent } from "react";

type Props = {
  columns: string[];
  rows: Record<string, string>[];
  onChange: (columns: string[], rows: Record<string, string>[]) => void;
};

const PAGE_SIZE = 1000;
const ROW_HEIGHT = 58;
const OVERSCAN_ROWS = 8;

export function EditableDataTable({ columns, rows, onChange }: Props) {
  const [query, setQuery] = useState("");
  const [sortColumn, setSortColumn] = useState<string>("");
  const [page, setPage] = useState(0);
  const [scrollTop, setScrollTop] = useState(0);
  const tableScrollRef = useRef<HTMLDivElement>(null);

  const safeColumns = columns.length ? columns : ["Column"];
  const filtered = useMemo(() => {
    const lower = query.toLowerCase();
    const base = rows.filter((row) => JSON.stringify(row).toLowerCase().includes(lower));
    if (!sortColumn) return base;
    return [...base].sort((a, b) => String(a[sortColumn] || "").localeCompare(String(b[sortColumn] || ""), undefined, { numeric: true }));
  }, [query, rows, sortColumn]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const pageRows = filtered.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE);
  const virtualStart = Math.max(0, Math.floor(scrollTop / ROW_HEIGHT) - OVERSCAN_ROWS);
  const virtualEnd = Math.min(pageRows.length, Math.ceil((scrollTop + 720) / ROW_HEIGHT) + OVERSCAN_ROWS);
  const visibleRows = pageRows.slice(virtualStart, virtualEnd);
  const topSpacerHeight = virtualStart * ROW_HEIGHT;
  const bottomSpacerHeight = Math.max(0, (pageRows.length - virtualEnd) * ROW_HEIGHT);
  const tableWidth = safeColumns.length * 240 + 120;

  function updateCell(rowIndex: number, column: string, value: string) {
    const originalIndex = rows.indexOf(visibleRows[rowIndex]);
    const next = [...rows];
    next[originalIndex] = { ...next[originalIndex], [column]: value };
    onChange(safeColumns, next);
  }

  function addRow() {
    onChange(safeColumns, [...rows, Object.fromEntries(safeColumns.map((column) => [column, ""]))]);
  }

  function deleteRow(rowIndex: number) {
    const target = visibleRows[rowIndex];
    onChange(safeColumns, rows.filter((row) => row !== target));
  }

  function removeLastRow() {
    if (!rows.length) return;
    onChange(safeColumns, rows.slice(0, -1));
  }

  function renameColumn(oldName: string, newName: string) {
    const clean = newName.trim();
    if (!clean || clean === oldName) return;
    const nextColumns = safeColumns.map((column) => (column === oldName ? clean : column));
    const nextRows = rows.map((row) => {
      const next = { ...row, [clean]: row[oldName] || "" };
      delete next[oldName];
      return next;
    });
    onChange(nextColumns, nextRows);
  }

  function addColumn() {
    const name = `Column ${safeColumns.length + 1}`;
    onChange([...safeColumns, name], rows.map((row) => ({ ...row, [name]: "" })));
  }

  function removeColumn(columnToRemove: string) {
    if (safeColumns.length <= 1) return;
    const nextColumns = safeColumns.filter((column) => column !== columnToRemove);
    const nextRows = rows.map((row) => {
      const next = { ...row };
      delete next[columnToRemove];
      return next;
    });
    onChange(nextColumns, nextRows);
  }

  function handleTableWheel(event: WheelEvent<HTMLDivElement>) {
    const tableScroller = tableScrollRef.current;
    if (!tableScroller) return;

    event.preventDefault();
    event.stopPropagation();

    if (event.shiftKey) {
      tableScroller.scrollLeft += event.deltaY || event.deltaX;
      return;
    }

    tableScroller.scrollTop += event.deltaY;
    tableScroller.scrollLeft += event.deltaX;
  }

  return (
    <div className="flex h-[calc(100vh-220px)] min-h-[520px] min-w-0 flex-col overflow-hidden">
      <div className="sticky top-0 z-20 mb-4 flex-shrink-0 rounded-2xl border border-slate-200 bg-white p-3 shadow-sm">
        <div className="flex flex-col gap-3 xl:flex-row xl:items-center xl:justify-between">
          <div className="min-w-0 flex-1">
            <label className="mb-2 block text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">Review Table</label>
            <input
              value={query}
              onChange={(event) => {
                setQuery(event.target.value);
                setPage(0);
              }}
              placeholder="Search rows, vendors, dates, totals..."
              className="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none ring-blue-100 transition placeholder:text-slate-400 focus:border-blue-500 focus:bg-white focus:ring-4"
            />
          </div>
          <div className="grid grid-cols-2 gap-2 sm:flex sm:items-center">
            <button onClick={addColumn} className="rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm font-semibold text-slate-700 hover:bg-slate-50">
              Add Column
            </button>
            <button onClick={addRow} className="rounded-xl bg-blue-600 px-4 py-3 text-sm font-semibold text-white shadow-sm hover:bg-blue-700">
              Add Row
            </button>
            <button onClick={removeLastRow} disabled={!rows.length} className="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm font-semibold text-rose-600 hover:bg-rose-100 disabled:cursor-not-allowed disabled:opacity-50">
              Remove Row
            </button>
          </div>
        </div>
        <p className="mt-3 text-xs text-slate-500">
          Tip: the scrollbars are inside the review box. Use them to move only table columns, rows, and headers.
        </p>
      </div>

      <div
        ref={tableScrollRef}
        onScroll={(event) => {
          setScrollTop(event.currentTarget.scrollTop);
        }}
        onWheel={handleTableWheel}
        className="min-h-0 w-full max-w-full flex-1 scroll-smooth overflow-x-auto overflow-y-auto overscroll-contain rounded-2xl border border-slate-200 bg-white shadow-sm [scrollbar-color:#94a3b8_#f1f5f9] [scrollbar-width:thin] [&::-webkit-scrollbar]:h-3 [&::-webkit-scrollbar]:w-3 [&::-webkit-scrollbar-thumb]:rounded-full [&::-webkit-scrollbar-thumb]:bg-slate-400 [&::-webkit-scrollbar-track]:bg-slate-100"
      >
        <table style={{ width: tableWidth }} className="min-w-full table-fixed border-collapse text-sm">
          <thead className="sticky top-0 z-30 bg-slate-50 shadow-sm">
            <tr>
              {safeColumns.map((column) => (
                <th key={column} className="w-[240px] min-w-[240px] whitespace-nowrap border-b border-slate-200 p-3 text-left">
                  <div className="flex w-full items-center gap-2">
                    <input
                      defaultValue={column}
                      onBlur={(event) => renameColumn(column, event.target.value)}
                      onClick={() => setSortColumn(column)}
                      className="min-w-0 flex-1 rounded-lg border border-transparent bg-transparent px-2 py-1 font-semibold text-slate-700 hover:border-slate-200"
                    />
                    <button
                      onClick={() => removeColumn(column)}
                      disabled={safeColumns.length <= 1}
                      className="rounded-md bg-rose-50 px-2 py-1 text-[11px] font-semibold text-rose-600 hover:bg-rose-100 disabled:cursor-not-allowed disabled:opacity-40"
                      title="Remove column"
                    >
                      Remove
                    </button>
                  </div>
                </th>
              ))}
              <th className="w-[120px] min-w-[120px] whitespace-nowrap border-b border-slate-200 p-3 text-left text-slate-700">Action</th>
            </tr>
          </thead>
          <tbody>
            {topSpacerHeight > 0 ? (
              <tr aria-hidden="true">
                <td colSpan={safeColumns.length + 1} style={{ height: topSpacerHeight }} className="border-0 p-0" />
              </tr>
            ) : null}
            {visibleRows.map((row, rowIndex) => (
              <tr key={`${page}-${virtualStart + rowIndex}`} className="h-[58px] odd:bg-slate-50/60 hover:bg-blue-50/50">
                {safeColumns.map((column) => (
                  <td key={column} className="w-[240px] min-w-[240px] whitespace-nowrap border-b border-slate-100 p-2">
                    <input
                      value={row[column] || ""}
                      onChange={(event) => updateCell(rowIndex, column, event.target.value)}
                      className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2.5 text-slate-900 outline-none transition focus:border-blue-500 focus:bg-white"
                    />
                  </td>
                ))}
                <td className="w-[120px] min-w-[120px] whitespace-nowrap border-b border-slate-100 p-2">
                  <button onClick={() => deleteRow(rowIndex)} className="rounded-lg bg-rose-50 px-3 py-2 text-xs font-semibold text-rose-600 hover:bg-rose-100">
                    Delete
                  </button>
                </td>
              </tr>
            ))}
            {bottomSpacerHeight > 0 ? (
              <tr aria-hidden="true">
                <td colSpan={safeColumns.length + 1} style={{ height: bottomSpacerHeight }} className="border-0 p-0" />
              </tr>
            ) : null}
          </tbody>
        </table>
      </div>

      <div className="mt-4 flex flex-shrink-0 flex-col gap-3 text-sm text-slate-500 sm:flex-row sm:items-center sm:justify-between">
        <span>
          Showing {pageRows.length ? virtualStart + 1 : 0}-{virtualStart + visibleRows.length} of {filtered.length} rows
        </span>
        <div className="flex items-center justify-between gap-2 sm:justify-end">
          <button disabled={page === 0} onClick={() => setPage((value) => Math.max(0, value - 1))} className="rounded-lg border border-slate-200 bg-white px-3 py-2 disabled:opacity-40">
            Prev
          </button>
          <span>
            {page + 1} / {totalPages}
          </span>
          <button disabled={page + 1 >= totalPages} onClick={() => setPage((value) => Math.min(totalPages - 1, value + 1))} className="rounded-lg border border-slate-200 bg-white px-3 py-2 disabled:opacity-40">
            Next
          </button>
        </div>
      </div>
    </div>
  );
}
