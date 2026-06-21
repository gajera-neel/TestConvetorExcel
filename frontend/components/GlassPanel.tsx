"use client";

import { motion } from "framer-motion";

export function GlassPanel({
  children,
  className = "",
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <motion.section
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35 }}
      className={`glass-card rounded-2xl p-4 sm:p-5 md:p-6 ${className}`}
    >
      {children}
    </motion.section>
  );
}
