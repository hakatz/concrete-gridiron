"use client";

import { useState } from "react";
import Link from "next/link";
import leagueData from "@/data/league_analytics.json";
import { Swords } from "lucide-react";

export default function H2HPage() {
  const { h2h_matrix, managers } = leagueData;
  const [selectedM1, setSelectedM1] = useState(managers[0]?.manager_id || "");
  const [selectedM2, setSelectedM2] = useState(managers[1]?.manager_id || "");

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
          <table className="w-full text-center text-xs border-collapse">
            <thead>
              <tr className="bg-slate-950/80 text-slate-400">
                <th className="p-2.5 text-left border border-slate-800 font-bold sticky left-0 bg-slate-950">
                  Manager
                </th>
                {managers.map((opp) => (
                  <th
                    key={opp.manager_id}
                    className="p-2.5 border border-slate-800 font-bold truncate max-w-[100px]"
                    title={opp.name}
                  >
                    {opp.name.split(" ")[0]}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {h2h_matrix.map((row) => (
                <tr key={row.manager_id} className="hover:bg-slate-800/20">
                  <td className="p-2.5 text-left font-bold text-white border border-slate-800 sticky left-0 bg-slate-900 truncate max-w-[140px]">
                    <Link href={`/managers/${row.manager_id}`} className="hover:text-emerald-400">
                      {row.manager_name}
                    </Link>
                  </td>
                  {managers.map((opp) => {
                    if (row.manager_id === opp.manager_id) {
                      return (
                        <td
                          key={opp.manager_id}
                          className="p-2.5 border border-slate-800/80 bg-slate-950/80 text-slate-700 font-black"
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
                    const cellClass = isWinning
                      ? "bg-emerald-500/10 text-emerald-300"
                      : isLosing
                      ? "bg-rose-500/10 text-rose-300"
                      : "text-slate-400";

                    return (
                      <td
                        key={opp.manager_id}
                        onClick={() => {
                          setSelectedM1(row.manager_id);
                          setSelectedM2(opp.manager_id);
                        }}
                        className={`p-2.5 border border-slate-800/80 cursor-pointer font-bold transition-colors ${cellClass}`}
                        title={`${row.manager_name} vs ${opp.name}: ${stats.wins}-${stats.losses}`}
                      >
                        {stats.wins}-{stats.losses}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
