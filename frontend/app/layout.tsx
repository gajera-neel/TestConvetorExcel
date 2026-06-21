import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Document to Excel AI",
  description: "Premium demo MVP for document intelligence and Excel conversion",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="floating-orb left-8 top-10 h-48 w-48 bg-violet-600/40" />
        <div className="floating-orb bottom-10 right-10 h-56 w-56 bg-cyan-500/30" />
        {children}
      </body>
    </html>
  );
}
