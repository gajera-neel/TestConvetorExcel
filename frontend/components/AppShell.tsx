"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";

const nav = [
  { href: "/dashboard", label: "Dashboard", index: "▦", short: "Dash" },
  { href: "/upload", label: "Upload", index: "▣", short: "Upload" },
  { href: "/excel-export", label: "Excel Export", index: "▤", short: "Excel" },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="min-h-screen bg-[#f5f7fb]">
      <div className="w-full">
        <motion.header
          initial={{ opacity: 0, y: -12 }}
          animate={{ opacity: 1, y: 0 }}
          className="sticky top-0 z-40 flex items-center justify-between border-b border-slate-200 bg-white/95 px-3 py-3 shadow-sm backdrop-blur lg:hidden"
        >
          <Link href="/upload" className="flex items-center gap-3">
            <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-blue-600 text-sm font-black text-white">
              AI
            </span>
            <span>
              <strong className="block leading-tight text-slate-950">DocExcel</strong>
              <small className="text-slate-500">AI Converter</small>
            </span>
          </Link>
          <span className="rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700">Business App</span>
        </motion.header>

        <div className="grid lg:grid-cols-[220px_1fr]">
        <motion.aside
          initial={{ opacity: 0, x: 0 }}
          animate={{ opacity: 1, x: 0 }}
          className="sticky top-0 hidden h-screen border-r border-slate-800 bg-[#08111f] p-3 text-white lg:block"
        >
          <div className="flex h-full flex-col">
            <div className="mb-5 px-2 pt-1">
              <div className="mb-3 flex items-center gap-2">
                <div className="flex h-8 w-8 items-center justify-center rounded-md bg-blue-600 text-xs font-black text-white">
                  AI
                </div>
                <div>
                  <h1 className="text-sm font-bold tracking-tight">DocExcel AI</h1>
                  <p className="text-[11px] text-slate-400">Business Automation</p>
                </div>
              </div>
            </div>

            <nav className="grid gap-1">
              {nav.map((item) => {
                const active = pathname === item.href;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`group flex items-center gap-3 rounded-lg border px-3 py-2.5 transition ${
                      active
                        ? "border-blue-600 bg-[#123760] text-white"
                        : "border-transparent text-slate-300 hover:bg-[#0f1d31] hover:text-white"
                    }`}
                  >
                    <span className={`flex h-7 w-7 items-center justify-center rounded-md text-[13px] ${active ? "bg-blue-500 text-white" : "bg-[#111c2d] text-slate-400"}`}>
                      {item.index}
                    </span>
                    <span className="text-sm font-semibold">{item.label}</span>
                  </Link>
                );
              })}
            </nav>

            <div className="mt-5 border-t border-slate-800 pt-4">
              <p className="px-3 text-xs font-semibold text-slate-400">Documents</p>
              <div className="mt-2 grid gap-1">
                {["Invoices", "Bills", "Receipts", "Exports"].map((item) => (
                  <div key={item} className="rounded-lg px-3 py-2 text-xs text-slate-400">
                    {item}
                  </div>
                ))}
              </div>
            </div>

            <div className="mt-auto rounded-lg bg-[#0f1d31] p-3">
              <p className="text-[11px] font-semibold uppercase tracking-[0.14em] text-blue-300">Account</p>
              <p className="mt-2 text-xs leading-5 text-slate-300">Local Demo Workspace</p>
            </div>
          </div>
        </motion.aside>

          <main className="min-w-0 bg-white p-3 pb-24 sm:p-5 sm:pb-24 lg:min-h-screen lg:p-6">{children}</main>
        </div>
      </div>

      <nav className="fixed inset-x-3 bottom-3 z-50 grid grid-cols-3 rounded-2xl border border-slate-200 bg-white/95 p-1.5 shadow-2xl shadow-slate-900/15 backdrop-blur lg:hidden">
        {nav.map((item) => {
          const active = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex flex-col items-center justify-center rounded-xl px-2 py-2 text-[11px] font-semibold transition ${
                active ? "bg-blue-600 text-white shadow-sm" : "text-slate-500 hover:bg-slate-50"
              }`}
            >
              <span className="text-sm leading-none">{item.index}</span>
              <span className="mt-1">{item.short}</span>
            </Link>
          );
        })}
      </nav>
    </div>
  );
}
