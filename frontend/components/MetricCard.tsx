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
      className="glass-card rounded-2xl p-5"
    >
      <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-xl bg-blue-50 text-blue-600">
        ●
      </div>
      <p className="text-sm text-slate-500">{label}</p>
      <strong className="mt-2 block text-3xl font-bold tracking-tight text-slate-950 sm:text-4xl">{value}</strong>
      {detail ? <span className="mt-2 block text-xs text-slate-500">{detail}</span> : null}
    </motion.div>
  );
}
