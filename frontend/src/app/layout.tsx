import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";
import { Trophy, Users, Swords, ScrollText, Calendar, Shield } from "lucide-react";

export const metadata: Metadata = {
  title: "Concrete Gridiron | Fantasy Football Historical Archive",
  description: "Comprehensive historical archive, manager tendencies, and record books for Yahoo Fantasy Football League 503435.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-gridiron-950 text-slate-100 antialiased flex flex-col">
        {/* Navigation Bar */}
        <header className="sticky top-0 z-50 border-b border-slate-800/80 bg-gridiron-950/90 backdrop-blur-md">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
            <Link href="/" className="flex items-center gap-3 group">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-500 to-emerald-600 flex items-center justify-center shadow-lg shadow-emerald-900/20 group-hover:scale-105 transition-transform">
                <Shield className="w-5 h-5 text-slate-950 font-bold" />
              </div>
              <div>
                <span className="font-extrabold text-lg tracking-tight text-white group-hover:text-emerald-400 transition-colors">
                  CONCRETE GRIDIRON
                </span>
                <span className="block text-xs font-semibold text-slate-400 tracking-wider uppercase">
                  Yahoo League #503435 Archive
                </span>
              </div>
            </Link>

            <nav className="flex items-center gap-1 sm:gap-2">
              <Link
                href="/"
                className="px-3 py-2 rounded-lg text-sm font-medium text-slate-300 hover:text-white hover:bg-slate-800/60 transition-colors flex items-center gap-2"
              >
                <Trophy className="w-4 h-4 text-amber-400" />
                <span>Dashboard</span>
              </Link>
              <Link
                href="/h2h"
                className="px-3 py-2 rounded-lg text-sm font-medium text-slate-300 hover:text-white hover:bg-slate-800/60 transition-colors flex items-center gap-2"
              >
                <Swords className="w-4 h-4 text-rose-400" />
                <span>H2H Matrix</span>
              </Link>
              <Link
                href="/drafts"
                className="px-3 py-2 rounded-lg text-sm font-medium text-slate-300 hover:text-white hover:bg-slate-800/60 transition-colors flex items-center gap-2"
              >
                <Calendar className="w-4 h-4 text-cyan-400" />
                <span>Draft Archive</span>
              </Link>
              <Link
                href="/rules"
                className="px-3 py-2 rounded-lg text-sm font-medium text-slate-300 hover:text-white hover:bg-slate-800/60 transition-colors flex items-center gap-2"
              >
                <ScrollText className="w-4 h-4 text-emerald-400" />
                <span>Constitution</span>
              </Link>
            </nav>
          </div>
        </header>

        {/* Main Content */}
        <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </main>

        {/* Footer */}
        <footer className="border-t border-slate-800/80 bg-gridiron-900/50 py-6 text-center text-xs text-slate-500">
          <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
            <p>© {new Date().getFullYear()} Concrete Gridiron Historical Archive. Playwright ETL & Analytics Engine.</p>
            <p className="text-slate-400 font-medium">Yahoo Fantasy Football ID #503435 • Active Season 2026</p>
          </div>
        </footer>
      </body>
    </html>
  );
}
