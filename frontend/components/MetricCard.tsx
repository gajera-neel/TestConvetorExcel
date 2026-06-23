"use client";

import { motion } from "framer-motion";

export function MetricCard({
  label,
  value,
  detail,
}: {
  label: string;
  value: string | number;
  detail?: string;
}) {
  return (
    <motion.div
      whileHover={{ y: -4, scale: 1.01 }}
      className="glass-card rounded-2xl p-4 sm:p-5"
    >
      <div className="mb-3 flex h-9 w-9 items-center justify-center rounded-xl bg-blue-50 text-blue-600 sm:mb-4 sm:h-10 sm:w-10">
        ●
      </div>
      <p className="text-sm text-slate-500">{label}</p>
      <strong className="mt-2 block break-words text-2xl font-bold tracking-tight text-slate-950 sm:text-4xl">{value}</strong>
      {detail ? <span className="mt-2 block text-xs text-slate-500">{detail}</span> : null}
    </motion.div>
  );
}
