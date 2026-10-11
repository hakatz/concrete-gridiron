#!/usr/bin/env python3
"""Writes TSX page files cleanly (no BOM, LF line endings)."""
import os

ROOT = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'src', 'app')

def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)
    print(f'Written: {path}')

# ---------------------------------------------------------------------------
# h2h/page.tsx
# ---------------------------------------------------------------------------
H2H = '''\
"use client";

import { useState } from "react";
import Link from "next/link";
import leagueData from "@/data/league_analytics.json";
import { Swords } from "lucide-react";

export default function H2HPage() {
  const { h2h_matrix, managers } = leagueData;
  const [selectedM1, setSelectedM1] = useState(managers[0]?.manager_id || "");
  const [selectedM2, setSelectedM2] = useState(managers[1]?.manager_id || "");
  const [hoveredRow, setHoveredRow] = useState<string | null>(null);
  const [hoveredCol, setHoveredCol] = useState<string | null>(null);

  const m1Data = managers.find((m) => m.manager_id === selectedM1);
  const m2Data = managers.find((m) => m.manager_id === selectedM2);

  const h2hRow = h2h_matrix.find((r) => r.manager_id === selectedM1);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const matchupStats = (h2hRow?.opponents as any)?.[selectedM2] || {
    wins: 0,
    losses: 0,
    ties: 0,
    pf: 0,
    pa: 0,
    total_games: 0,
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2">
          <Swords className="w-7 h-7 text-rose-500" />
          <h1 className="text-3xl font-black text-white tracking-tight">HEAD-TO-HEAD MATRIX</h1>
        </div>
        <p className="text-slate-400 text-sm mt-1">
          Complete career rivalry records across all regular season and playoff matchups in league history.
        </p>
      </div>

      {/* Interactive Head-to-Head Spotlight Comparison */}
      <div className="rounded-2xl bg-gradient-to-r from-slate-900 via-gridiron-900 to-slate-900 border border-slate-800 p-6 shadow-2xl space-y-6">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 border-b border-slate-800 pb-4">
          <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
            Select Two Managers to Compare
          </span>
          <div className="flex items-center gap-3">
            <select
              value={selectedM1}
              onChange={(e) => setSelectedM1(e.target.value)}
              className="bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-sm text-white focus:outline-none focus:border-emerald-500"
            >
              {managers.map((m) => (
                <option key={m.manager_id} value={m.manager_id}>
                  {m.name}
                </option>
              ))}
            </select>
            <span className="text-slate-500 font-black">VS</span>
            <select
              value={selectedM2}
              onChange={(e) => setSelectedM2(e.target.value)}
              className="bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-sm text-white focus:outline-none focus:border-rose-500"
            >
              {managers.map((m) => (
                <option key={m.manager_id} value={m.manager_id} disabled={m.manager_id === selectedM1}>
                  {m.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Rivalry Comparison Cards */}
        {selectedM1 !== selectedM2 && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-center">
            {/* Manager 1 */}
            <div className="bg-slate-950/60 border border-slate-800 rounded-xl p-5 text-center space-y-2">
              <span className="text-xs font-bold text-emerald-400 uppercase">Manager 1</span>
              <p className="text-xl font-black text-white">{m1Data?.name}</p>
              <div className="text-2xl font-black text-emerald-400">
                {matchupStats.wins} {matchupStats.wins === 1 ? "Win" : "Wins"}
              </div>
              <p className="text-xs text-slate-400">{matchupStats.pf.toFixed(1)} Total Pts Scored</p>
            </div>

            {/* Matchup Summary Badge */}
            <div className="bg-slate-900/80 border border-slate-800/80 rounded-xl p-4 text-center space-y-2">
              <span className="text-[11px] font-bold text-slate-400 uppercase tracking-widest">
                Career Series
              </span>
              <div className="text-3xl font-black text-white tracking-wider">
                {matchupStats.wins} - {matchupStats.losses}
                {matchupStats.ties > 0 ? ` - ${matchupStats.ties}T` : ""}
              </div>
              <p className="text-xs text-slate-400">{matchupStats.total_games} Total Matchups Played</p>
              <p className="text-xs font-bold text-cyan-400">
                Avg Differential:{" "}
                {matchupStats.total_games > 0
                  ? Math.abs((matchupStats.pf - matchupStats.pa) / matchupStats.total_games).toFixed(1)
                  : "0.0"}{" "}
                pts/game
              </p>
            </div>

            {/* Manager 2 */}
            <div className="bg-slate-950/60 border border-slate-800 rounded-xl p-5 text-center space-y-2">
              <span className="text-xs font-bold text-rose-400 uppercase">Manager 2</span>
              <p className="text-xl font-black text-white">{m2Data?.name}</p>
              <div className="text-2xl font-black text-rose-400">
                {matchupStats.losses} {matchupStats.losses === 1 ? "Win" : "Wins"}
              </div>
              <p className="text-xs text-slate-400">{matchupStats.pa.toFixed(1)} Total Pts Scored</p>
            </div>
          </div>
        )}
      </div>

      {/* NxN All-Time Head-to-Head Table */}
      <div className="rounded-2xl bg-slate-900/60 border border-slate-800 overflow-hidden shadow-xl space-y-4 p-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-4">
          <div>
            <h2 className="text-lg font-bold text-white tracking-tight">Full Head-to-Head Grid</h2>
            <p className="text-xs text-slate-400">
              Read horizontally: Row Manager&apos;s record against Column Opponent (Wins - Losses)
            </p>
          </div>
          <div className="flex items-center gap-3 text-xs">
            <span className="flex items-center gap-1">
              <span className="w-3 h-3 rounded-full bg-emerald-500/20 border border-emerald-500/40 inline-block" />
              <span className="text-emerald-400 font-semibold">Winning</span>
            </span>
            <span className="flex items-center gap-1">
              <span className="w-3 h-3 rounded-full bg-rose-500/20 border border-rose-500/40 inline-block" />
              <span className="text-rose-400 font-semibold">Losing</span>
            </span>
            <span className="flex items-center gap-1">
              <span className="w-3 h-3 rounded-full bg-slate-800 border border-slate-700 inline-block" />
              <span className="text-slate-400 font-semibold">Even</span>
            </span>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table
            className="w-full text-center text-xs border-collapse"
            onMouseLeave={() => {
              setHoveredRow(null);
              setHoveredCol(null);
            }}
          >
            <thead>
              <tr className="bg-slate-950/80 text-slate-400">
                <th className="p-2.5 text-left border border-slate-800 font-bold sticky left-0 bg-slate-950">
                  Manager
                </th>
                {managers.map((opp) => {
                  const isColHighlighted = hoveredCol === opp.manager_id;
                  return (
                    <th
                      key={opp.manager_id}
                      className={`p-2.5 border border-slate-800 font-bold truncate max-w-[100px] transition-colors ${
                        isColHighlighted ? "bg-slate-800 text-white border-b-cyan-500 font-black" : ""
                      }`}
                      title={opp.name}
                    >
                      {opp.name.split(" ")[0]}
                    </th>
                  );
                })}
              </tr>
            </thead>
            <tbody>
              {h2h_matrix.map((row) => {
                const isRowHighlighted = hoveredRow === row.manager_id;
                return (
                  <tr
                    key={row.manager_id}
                    className={`transition-colors ${isRowHighlighted ? "bg-slate-800/40" : ""}`}
                  >
                    <td
                      className={`p-2.5 text-left font-bold border border-slate-800 sticky left-0 truncate max-w-[140px] transition-colors ${
                        isRowHighlighted ? "bg-slate-800 text-cyan-300 font-black" : "bg-slate-900 text-white"
                      }`}
                    >
                      <Link href={`/managers/${row.manager_id}`} className="hover:text-emerald-400">
                        {row.manager_name}
                      </Link>
                    </td>
                    {managers.map((opp) => {
                      const isColHighlighted = hoveredCol === opp.manager_id;
                      const isIntersected = isRowHighlighted && isColHighlighted;

                      if (row.manager_id === opp.manager_id) {
                        return (
                          <td
                            key={opp.manager_id}
                            onMouseEnter={() => {
                              setHoveredRow(row.manager_id);
                              setHoveredCol(opp.manager_id);
                            }}
                            className={`p-2.5 border border-slate-800/80 text-slate-700 font-black transition-colors ${
                              isIntersected ? "bg-slate-800 text-slate-500" : isRowHighlighted || isColHighlighted ? "bg-slate-900/90 text-slate-600" : "bg-slate-950/80"
                            }`}
                          >
                            —
                          </td>
                        );
                      }
                      // eslint-disable-next-line @typescript-eslint/no-explicit-any
                      const stats = (row.opponents as any)?.[opp.manager_id] || {
                        wins: 0,
                        losses: 0,
                        ties: 0,
                      };
                      const isWinning = stats.wins > stats.losses;
                      const isLosing = stats.losses > stats.wins;

                      let cellBg = isWinning
                        ? "bg-emerald-500/10 text-emerald-300"
                        : isLosing
                        ? "bg-rose-500/10 text-rose-300"
                        : "text-slate-400";

                      if (isIntersected) {
                        cellBg += " ring-2 ring-cyan-400 bg-cyan-950/70 font-black z-10 scale-105 shadow-md";
                      } else if (isRowHighlighted || isColHighlighted) {
                        cellBg += " brightness-125 bg-slate-800/60";
                      }

                      return (
                        <td
                          key={opp.manager_id}
                          onMouseEnter={() => {
                            setHoveredRow(row.manager_id);
                            setHoveredCol(opp.manager_id);
                          }}
                          onClick={() => {
                            setSelectedM1(row.manager_id);
                            setSelectedM2(opp.manager_id);
                          }}
                          className={`p-2.5 border border-slate-800/80 cursor-pointer font-bold transition-all relative ${cellBg}`}
                          title={`${row.manager_name} vs ${opp.name}: ${stats.wins}-${stats.losses}`}
                        >
                          {stats.wins}-{stats.losses}
                        </td>
                      );
                    })}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
'''

# ---------------------------------------------------------------------------
# managers/[id]/page.tsx
# ---------------------------------------------------------------------------
MANAGER = '''\
import Link from "next/link";
import { notFound } from "next/navigation";
import leagueData from "@/data/league_analytics.json";
import {
  Trophy,
  Swords,
  Skull,
  Award,
  ArrowLeft,
  RefreshCw,
  ExternalLink,
} from "lucide-react";
import ManagerCharts from "./ManagerCharts";

const ARCHETYPE_DESCRIPTIONS: Record<string, string> = {
  "Dynasty Architect": "Won 3+ championships across their career",
  "Waiver Wire Hawk": "Averages 25+ waiver moves per season",
  "Draft-and-Hold Purist": "Rarely makes waiver moves; trusts their draft",
  "Blockbuster Trader": "Averages 1.5+ trades per season",
  "High Roster Loyalty": "Retains 60%+ of drafted players to end of season",
  "Extreme Roster Churner": "Turns over 65%+ of drafted players via waivers",
  "Zero-RB Disciple": "Avoids RBs early, loads up on WRs/TEs in rounds 1-3",
  "Bellcow Heavy": "Drafts RBs early and often in rounds 1-3",
  "Gunslinger QB Priority": "Drafts QB in early rounds most seasons",
  "Late QB Streamer": "Consistently waits until late rounds to draft QB",
  "Favored by Fortune": "Won 4+ more games than expected based on points scored",
  "Bad Beat Sufferer": "Lost 4+ more games than expected based on points scored",
  "Balanced Tactician": "Versatile manager; no single dominant tendency",
};

export function generateStaticParams() {
  return leagueData.managers.map((m) => ({
    id: m.manager_id,
  }));
}

export default async function ManagerDossierPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id: managerId } = await params;

  const rawManager = leagueData.managers.find((m) => m.manager_id === managerId);
  if (!rawManager) {
    notFound();
  }
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const manager = rawManager as any;

  const radarData = [
    { subject: "Zero-RB", value: manager.tendencies.zero_rb, fullMark: 100 },
    { subject: "Hero-RB", value: manager.tendencies.hero_rb, fullMark: 100 },
    { subject: "Early QB", value: manager.tendencies.early_qb, fullMark: 100 },
    { subject: "Late Stream", value: manager.tendencies.late_streamer, fullMark: 100 },
    { subject: "Reaches", value: manager.tendencies.reach_frequency, fullMark: 100 },
    { subject: "Steals", value: manager.tendencies.steal_efficiency, fullMark: 100 },
    {
      subject: "Waiver Churn",
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      value: (manager.tendencies as any).waiver_activity ?? 50,
      fullMark: 100,
    },
  ];

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const t = manager.tendencies as any;
  const r1_3 = t.pos_allocation_r1_3 || {};
  const r4_7 = t.pos_allocation_r4_7 || {};
  const r8_plus = t.pos_allocation_r8_plus || {};

  const barData = [
    {
      phase: "Rounds 1-3",
      RB: r1_3.RB || 0,
      WR: r1_3.WR || 0,
      QB: r1_3.QB || 0,
      TE: r1_3.TE || 0,
    },
    {
      phase: "Rounds 4-7",
      RB: r4_7.RB || 0,
      WR: r4_7.WR || 0,
      QB: r4_7.QB || 0,
      TE: r4_7.TE || 0,
    },
    {
      phase: "Rounds 8+",
      RB: r8_plus.RB || 0,
      WR: r8_plus.WR || 0,
      QB: r8_plus.QB || 0,
      TE: r8_plus.TE || 0,
    },
  ];

  const luckColor =
    manager.career.luck_diff > 0
      ? "text-emerald-400"
      : manager.career.luck_diff < 0
      ? "text-rose-400"
      : "text-slate-400";

  return (
    <div className="space-y-8">
      <Link
        href="/"
        className="inline-flex items-center gap-2 text-sm text-slate-400 hover:text-white transition-colors"
      >
        <ArrowLeft className="w-4 h-4" /> Back to Dashboard
      </Link>

      {/* Hero card */}
      <div className="relative rounded-2xl bg-gradient-to-r from-slate-900 via-gridiron-900 to-slate-900 border border-slate-800 p-6 sm:p-8 shadow-2xl">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-emerald-500 to-cyan-600 flex items-center justify-center text-2xl font-black text-slate-950 shadow-xl">
              {manager.name.charAt(0)}
            </div>
            <div>
              <div className="flex flex-wrap items-center gap-2">
                <h1 className="text-2xl sm:text-3xl font-black text-white">{manager.name}</h1>
                {manager.career.championships > 0 && (
                  <span className="px-2.5 py-0.5 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs font-bold flex items-center gap-1">
                    <Trophy className="w-3.5 h-3.5" />
                    {manager.career.championships}{" "}
                    {manager.career.championships === 1 ? "Champion" : "x Champion"}
                  </span>
                )}
              </div>
              <div className="flex flex-wrap items-center gap-3 mt-1">
                <p className="text-xs text-slate-400">
                  Historical Manager Dossier &bull; {manager.career.seasons} Seasons Active
                </p>
                {manager.yahoo_profile_url && (
                  <a
                    href={manager.yahoo_profile_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-400 border border-cyan-500/20 text-xs font-semibold transition-colors"
                  >
                    <ExternalLink className="w-3 h-3" /> Yahoo Profile
                  </a>
                )}
              </div>
              <div className="flex flex-wrap gap-1.5 mt-3">
                {(manager.archetypes || []).map((arch: string) => (
                  <span
                    key={arch}
                    title={ARCHETYPE_DESCRIPTIONS[arch] || arch}
                    className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-800 text-emerald-400 border border-slate-700 cursor-help"
                  >
                    {arch}
                  </span>
                ))}
              </div>
            </div>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="bg-slate-950/60 border border-slate-800 rounded-xl p-3 text-center">
              <span className="text-xs text-slate-500 uppercase font-semibold">Reg Season Record</span>
              <p className="text-lg font-black text-white">
                {manager.career.wins}-{manager.career.losses}
                {manager.career.ties > 0 ? `-${manager.career.ties}T` : ""}
              </p>
              <span className="text-xs text-emerald-400 font-bold">{manager.career.win_pct}% Win</span>
            </div>
            <div className="bg-slate-950/60 border border-slate-800 rounded-xl p-3 text-center">
              <span className="text-xs text-slate-500 uppercase font-semibold">Playoff Record</span>
              <p className="text-lg font-black text-amber-400">
                {manager.career.playoff_wins}-{manager.career.playoff_losses}
              </p>
              <span className="text-xs text-slate-400">{manager.career.playoff_appearances} Appearances</span>
            </div>
            <div className="bg-slate-950/60 border border-slate-800 rounded-xl p-3 text-center">
              <span className="text-xs text-slate-500 uppercase font-semibold">Avg Points/G</span>
              <p className="text-lg font-black text-cyan-400">{manager.career.avg_pf_per_game}</p>
              <span className="text-xs text-slate-400">High: {manager.career.high_score.toFixed(1)}</span>
            </div>
            <div className="bg-slate-950/60 border border-slate-800 rounded-xl p-3 text-center">
              <span className="text-xs text-slate-500 uppercase font-semibold">Luck Index</span>
              <p className={`text-lg font-black ${luckColor}`}>
                {manager.career.luck_diff > 0 ? "+" : ""}
                {manager.career.luck_diff}
              </p>
              <span className="text-xs text-slate-400">vs Expected Wins</span>
            </div>
          </div>
        </div>
      </div>

      {/* Nemesis & Victim */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="rounded-xl bg-gradient-to-br from-rose-950/30 to-slate-900/60 border border-rose-900/30 p-5 shadow-lg flex items-center justify-between">
          <div className="space-y-1">
            <span className="text-xs font-bold text-rose-400 uppercase tracking-wider flex items-center gap-1.5">
              <Skull className="w-4 h-4" /> Prime Nemesis
            </span>
            <p className="text-lg font-black text-white">
              {manager.nemesis ? (
                <Link href={`/managers/${manager.nemesis.manager_id}`} className="hover:text-rose-400">
                  {manager.nemesis.name}
                </Link>
              ) : (
                "None Yet"
              )}
            </p>
            <p className="text-xs text-slate-400">
              {manager.nemesis
                ? `Record: ${manager.nemesis.record} (${manager.nemesis.loss_pct}% loss rate)`
                : "Balanced matchups"}
            </p>
          </div>
          <div className="w-12 h-12 rounded-xl bg-rose-500/10 border border-rose-500/20 flex items-center justify-center text-rose-400">
            <Swords className="w-6 h-6" />
          </div>
        </div>

        <div className="rounded-xl bg-gradient-to-br from-emerald-950/30 to-slate-900/60 border border-emerald-900/30 p-5 shadow-lg flex items-center justify-between">
          <div className="space-y-1">
            <span className="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-1.5">
              <Award className="w-4 h-4" /> Favorite Victim
            </span>
            <p className="text-lg font-black text-white">
              {manager.victim ? (
                <Link href={`/managers/${manager.victim.manager_id}`} className="hover:text-emerald-400">
                  {manager.victim.name}
                </Link>
              ) : (
                "None Yet"
              )}
            </p>
            <p className="text-xs text-slate-400">
              {manager.victim
                ? `Record: ${manager.victim.record} (${manager.victim.win_pct}% win rate)`
                : "Balanced matchups"}
            </p>
          </div>
          <div className="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
            <Trophy className="w-6 h-6" />
          </div>
        </div>
      </div>

      {/* Charts */}
      <ManagerCharts
        managerName={manager.name}
        radarData={radarData}
        barData={barData}
      />

      {/* Waiver Wire Activity */}
      <div className="rounded-xl bg-slate-900/60 border border-slate-800 p-6 shadow-xl space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800 pb-4">
          <div>
            <h3 className="text-base font-bold text-white tracking-tight flex items-center gap-2">
              <RefreshCw className="w-4 h-4 text-purple-400" /> Waiver Wire Activity &amp; Roster Retention
            </h3>
            <p className="text-xs text-slate-400">
              Free agency churn, total moves, and key in-season waiver pickups
            </p>
          </div>
          <div className="flex items-center gap-4 text-xs font-semibold">
            <div>
              <span className="text-slate-500 uppercase">Total Moves: </span>
              <span className="text-white font-black">{manager.career.total_moves}</span>
            </div>
            <div>
              <span className="text-slate-500 uppercase">Trades: </span>
              <span className="text-amber-400 font-black">{manager.career.total_trades}</span>
            </div>
            <div>
              <span className="text-slate-500 uppercase">Retention: </span>
              <span className="text-purple-400 font-black">{manager.career.roster_retention_rate}%</span>
            </div>
          </div>
        </div>

        <div>
          <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">
            Top In-Season Waiver Pickups Finished on Roster
          </h4>
          {manager.waiver_gems && manager.waiver_gems.length > 0 ? (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-3">
              {manager.waiver_gems.map((gem: any, i: number) => (
                <div key={i} className="bg-slate-950/70 border border-slate-800 rounded-xl p-3 text-center">
                  <span className="text-xs font-bold text-white truncate block">{gem.player}</span>
                  <span className="text-[10px] font-bold text-purple-400">
                    {gem.pos} &bull; Yr {gem.year}
                  </span>
                  <p className="text-sm font-black text-emerald-400 mt-1">{gem.pts.toFixed(1)} Pts</p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-slate-500 italic">No significant late-season waiver gems recorded.</p>
          )}
        </div>
      </div>

      {/* Season Log */}
      <div className="rounded-xl bg-slate-900/60 border border-slate-800 overflow-hidden shadow-xl">
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between">
          <h3 className="text-sm font-bold text-slate-300 uppercase tracking-wider">
            Historical Season-by-Season Log
          </h3>
          <span className="text-xs text-slate-500">{(manager.historical_teams || []).length} Seasons</span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-950/70 text-slate-400 uppercase text-xs border-b border-slate-800">
              <tr>
                <th className="py-3 px-4">Season</th>
                <th className="py-3 px-4">Team Name</th>
                <th className="py-3 px-4 text-center">Finish</th>
                <th className="py-3 px-4 text-center">Record</th>
                <th className="py-3 px-4 text-right">Points For</th>
                <th className="py-3 px-4 text-right">Points Against</th>
                <th className="py-3 px-4 text-center">Moves</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {(manager.historical_teams || []).map((ht: any) => (
                <tr key={ht.year} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-3 px-4 font-bold text-white">{ht.year}</td>
                  <td className="py-3 px-4 italic text-slate-300">{ht.name}</td>
                  <td className="py-3 px-4 text-center font-bold text-amber-400">
                    {ht.rank === 1
                      ? "🏆 1st"
                      : ht.rank === 2
                      ? "🥈 2nd"
                      : ht.rank === 3
                      ? "🥉 3rd"
                      : `${ht.rank}th`}
                  </td>
                  <td className="py-3 px-4 text-center font-semibold">
                    {ht.wins}-{ht.losses}
                  </td>
                  <td className="py-3 px-4 text-right text-slate-300">{ht.pf.toFixed(1)}</td>
                  <td className="py-3 px-4 text-right text-slate-400">{ht.pa.toFixed(1)}</td>
                  <td className="py-3 px-4 text-center text-slate-400">{ht.moves || 0}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
'''

# ---------------------------------------------------------------------------
# rules/page.tsx
# ---------------------------------------------------------------------------
RULES = '''\
export default function RulesPage() {
  return (
    <div className="space-y-8 max-w-4xl">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-black text-white tracking-tight">LEAGUE CONSTITUTION</h1>
        <p className="text-slate-400 text-sm mt-1">
          Official rules and scoring settings for Concrete Gridiron Fantasy Football.
        </p>
      </div>

      {/* Roster Format */}
      <div className="rounded-2xl bg-slate-900/60 border border-slate-800 p-6 shadow-xl space-y-4">
        <h2 className="text-lg font-bold text-white border-b border-slate-800 pb-3">Roster Format</h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-sm">
          {[
            { slot: "QB", count: 1 },
            { slot: "RB", count: 2 },
            { slot: "WR", count: 2 },
            { slot: "TE", count: 1 },
            { slot: "FLEX (RB/WR/TE)", count: 1 },
            { slot: "K", count: 1 },
            { slot: "DEF/ST", count: 1 },
            { slot: "BN", count: 6 },
          ].map((row) => (
            <div
              key={row.slot}
              className="bg-slate-950/60 border border-slate-800 rounded-xl p-3 flex items-center justify-between"
            >
              <span className="font-bold text-white">{row.slot}</span>
              <span className="text-emerald-400 font-black">{row.count}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Scoring */}
      <div className="rounded-2xl bg-slate-900/60 border border-slate-800 p-6 shadow-xl space-y-4">
        <h2 className="text-lg font-bold text-white border-b border-slate-800 pb-3">Scoring (Half-PPR)</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-8 gap-y-2 text-sm text-slate-300">
          {[
            ["Passing TD", "+4 pts"],
            ["Passing Yard", "+0.04 pts (25 yds = 1 pt)"],
            ["INT Thrown", "-2 pts"],
            ["Rushing TD", "+6 pts"],
            ["Rushing Yard", "+0.1 pts (10 yds = 1 pt)"],
            ["Receiving TD", "+6 pts"],
            ["Receiving Yard", "+0.1 pts"],
            ["Reception", "+0.5 pts (half-PPR)"],
            ["Fumble Lost", "-2 pts"],
            ["2-Pt Conversion", "+2 pts"],
            ["FG Made (0-39 yds)", "+3 pts"],
            ["FG Made (40-49 yds)", "+4 pts"],
            ["FG Made (50+ yds)", "+5 pts"],
            ["XP Made", "+1 pt"],
            ["DEF Sack", "+1 pt"],
            ["DEF INT", "+2 pts"],
            ["DEF TD", "+6 pts"],
            ["DEF Shutout", "+10 pts"],
          ].map(([label, value]) => (
            <div key={label} className="flex justify-between border-b border-slate-800/50 py-1.5">
              <span className="text-slate-400">{label}</span>
              <span className="font-semibold text-white">{value}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Waivers */}
      <div className="rounded-2xl bg-slate-900/60 border border-slate-800 p-6 shadow-xl space-y-3">
        <h2 className="text-lg font-bold text-white border-b border-slate-800 pb-3">
          Waivers &amp; Free Agency (FAAB)
        </h2>
        <ul className="space-y-2 text-sm text-slate-300 list-disc list-inside">
          <li>Free Agent Acquisition Budget (FAAB): <strong className="text-white">$100</strong> per season</li>
          <li>Waiver claims processed: <strong className="text-white">Wednesday morning</strong></li>
          <li>After waivers clear, remaining free agents may be added immediately (no bid)</li>
          <li>Dropped players go on waivers for <strong className="text-white">2 days</strong> before becoming free agents</li>
          <li>No FAAB rollover between seasons</li>
        </ul>
      </div>

      {/* Playoffs */}
      <div className="rounded-2xl bg-slate-900/60 border border-slate-800 p-6 shadow-xl space-y-3">
        <h2 className="text-lg font-bold text-white border-b border-slate-800 pb-3">Playoffs</h2>
        <ul className="space-y-2 text-sm text-slate-300 list-disc list-inside">
          <li>Regular season: <strong className="text-white">14 weeks</strong> (Weeks 1-14)</li>
          <li>Playoffs: <strong className="text-white">Weeks 15-17</strong> (3 rounds)</li>
          <li><strong className="text-white">6 teams</strong> qualify (top 6 by record, then PF as tiebreaker)</li>
          <li>Week 15: Seeds 3v6, 4v5 (first round byes for seeds 1-2)</li>
          <li>Week 16: Semifinals</li>
          <li>Week 17: Championship</li>
        </ul>
      </div>

      {/* Last Place Punishment */}
      <div className="rounded-2xl bg-gradient-to-r from-rose-950/30 to-slate-900/60 border border-rose-900/30 p-6 shadow-xl space-y-3">
        <h2 className="text-lg font-bold text-rose-400 border-b border-rose-900/40 pb-3">
          Last Place Punishment
        </h2>
        <p className="text-sm text-slate-300">
          The manager finishing in last place (12th) earns the last place punishment — 
          a rotating punishment determined by a vote of all league members before the following season.
          Past punishments have included eating disgusting food combinations on video, 
          posting embarrassing photos, and public pledges.
        </p>
        <p className="text-sm text-slate-400 italic">
          The shame lives in the record books forever.
        </p>
      </div>
    </div>
  );
}
'''

write(os.path.join(ROOT, 'h2h', 'page.tsx'), H2H)
write(os.path.join(ROOT, 'managers', '[id]', 'page.tsx'), MANAGER)
write(os.path.join(ROOT, 'rules', 'page.tsx'), RULES)
print('All pages written successfully.')
