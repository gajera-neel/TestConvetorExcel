"use client";

import { motion } from "framer-motion";
import type { ChartPoint } from "@/lib/types";

function labelOf(item: ChartPoint) {
  return item.label || item.day || item.detected_type || "Data";
}

function valueOf(item: ChartPoint) {
  return Number(item.value ?? item.count ?? item.amount ?? 0);
}

export function ChartBars({ title, data }: { title: string; data: ChartPoint[] }) {
  const max = Math.max(...data.map(valueOf), 1);

  return (
    <div className="glass-card rounded-2xl p-5">
      <div className="mb-5 flex items-center justify-between">
        <h3 className="text-lg font-semibold">{title}</h3>
        <span className="text-xs text-slate-500">Live</span>
      </div>
      {data.length === 0 ? (
        <div className="rounded-xl border border-dashed border-slate-300 bg-slate-50 p-5 text-sm text-slate-500">
          No data yet. Upload files to generate this chart.
        </div>
      ) : (
      <div className="grid gap-4">
        {data.map((item, index) => {
          const value = valueOf(item);
          return (
            <div key={`${labelOf(item)}-${index}`} className="grid grid-cols-[82px_1fr_48px] items-center gap-2 text-xs sm:grid-cols-[110px_1fr_70px] sm:gap-3 sm:text-sm">
              <span className="truncate text-slate-600">{labelOf(item)}</span>
              <div className="h-3 overflow-hidden rounded-full bg-slate-100">
                <motion.i
                  initial={{ width: 0 }}
                  animate={{ width: `${(value / max) * 100}%` }}
                  className="block h-full rounded-full bg-blue-600"
                />
              </div>
              <strong className="text-right text-slate-800">{value}</strong>
            </div>
          );
        })}
      </div>
      )}
    </div>
  );
}
