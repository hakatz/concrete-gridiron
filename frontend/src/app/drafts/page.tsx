"use client";

import { useState } from "react";
import leagueData from "@/data/league_analytics.json";
import { Calendar, Search, TrendingDown, TrendingUp } from "lucide-react";

export default function DraftsPage() {
  const { draft_archive, historical_seasons, managers } = leagueData;
  const [selectedYear, setSelectedYear] = useState<number>(historical_seasons[historical_seasons.length - 1] || 2024);
  const [posFilter, setPosFilter] = useState<string>("ALL");
  const [managerFilter, setManagerFilter] = useState<string>("ALL");
  const [searchQuery, setSearchQuery] = useState<string>("");

  const filteredPicks = draft_archive.filter((p) => {
    if (p.year !== selectedYear) return false;
    if (posFilter !== "ALL" && p.position !== posFilter) return false;
    if (managerFilter !== "ALL" && p.manager_name !== managerFilter) return false;
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      return p.player_name.toLowerCase().includes(q) || p.manager_name.toLowerCase().includes(q);
    }
    return true;
  });

  const getPositionBadge = (pos: string) => {
    switch (pos) {
      case "RB": return "bg-emerald-500/10 text-emerald-400 border-emerald-500/20";
      case "WR": return "bg-blue-500/10 text-blue-400 border-blue-500/20";
      case "QB": return "bg-amber-500/10 text-amber-400 border-amber-500/20";
      case "TE": return "bg-purple-500/10 text-purple-400 border-purple-500/20";
      default: return "bg-slate-800 text-slate-400 border-slate-700";
    }
  };

  return (
    <div className="space-y-8">
      <div>
        <div className="flex items-center gap-2">
          <Calendar className="w-7 h-7 text-cyan-400" />
          <h1 className="text-3xl font-black text-white tracking-tight">HISTORICAL DRAFT ARCHIVE</h1>
        </div>
        <p className="text-slate-400 text-sm mt-1">
          Historical round-by-round draft boards from 2014 to 2025, color-coded by position with reach and steal callouts.
        </p>
      </div>

      <div className="rounded-2xl bg-slate-900/70 border border-slate-800 p-6 shadow-xl space-y-4">
        <div className="flex items-center gap-2 overflow-x-auto pb-2">
          {historical_seasons.map((yr) => (
            <button
              key={yr}
              onClick={() => setSelectedYear(yr)}
              className={"px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all shrink-0 " + (
                selectedYear === yr
                  ? "bg-emerald-500 text-slate-950 shadow-lg shadow-emerald-500/20"
                  : "bg-slate-800 text-slate-300 hover:bg-slate-700 hover:text-white"
              )}
            >
              {yr}
            </button>
          ))}
        </div>

        <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-2 border-t border-slate-800">
          <div className="flex items-center gap-1.5 w-full sm:w-auto overflow-x-auto">
            {["ALL", "RB", "WR", "QB", "TE", "DEF", "K"].map((p) => (
              <button
                key={p}
                onClick={() => setPosFilter(p)}
                className={"px-2.5 py-1 rounded-md text-xs font-semibold transition-colors " + (
                  posFilter === p
                    ? "bg-cyan-500/20 text-cyan-400 border border-cyan-500/40"
                    : "text-slate-400 hover:text-slate-200"
                )}
              >
                {p}
              </button>
            ))}
          </div>

          <div className="flex flex-col sm:flex-row items-center gap-2 w-full sm:w-auto">
            <select
              value={managerFilter}
              onChange={(e) => setManagerFilter(e.target.value)}
              className="bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-emerald-500 w-full sm:w-auto"
            >
              <option value="ALL">All Managers</option>
              {managers.map((m) => (
                <option key={m.manager_id} value={m.name}>
                  {m.name}
                </option>
              ))}
            </select>

            <div className="relative w-full sm:w-56">
              <Search className="w-4 h-4 text-slate-500 absolute left-3 top-2 pointer-events-none" />
              <input
                type="text"
                placeholder="Search player..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-slate-950 border border-slate-700 rounded-lg pl-9 pr-3 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500"
              />
            </div>
          </div>
        </div>
      </div>

      <div className="rounded-2xl bg-slate-900/60 border border-slate-800 overflow-hidden shadow-xl">
        <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between">
          <h2 className="text-sm font-bold text-slate-300 uppercase tracking-wider">
            {selectedYear} Draft Board • {filteredPicks.length} Total Picks Shown
          </h2>
          <div className="flex items-center gap-4 text-xs">
            <span className="flex items-center gap-1 text-emerald-400 font-semibold">
              <TrendingUp className="w-3.5 h-3.5" /> Steal (Outperformed draft by 10+ spots)
            </span>
            <span className="flex items-center gap-1 text-rose-400 font-semibold">
              <TrendingDown className="w-3.5 h-3.5" /> Reach (Underperformed draft by 10+ spots)
            </span>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-950/70 text-slate-400 uppercase text-xs border-b border-slate-800">
              <tr>
                <th className="py-3 px-4 text-center">Pick</th>
                <th className="py-3 px-4 text-center">Round</th>
                <th className="py-3 px-4">Player</th>
                <th className="py-3 px-4 text-center">Pos</th>
                <th className="py-3 px-4">Drafted By (Manager)</th>
                <th className="py-3 px-4 text-slate-500">Team Name</th>
                <th className="py-3 px-4 text-right">Season Pts</th>
                <th className="py-3 px-4 text-right">Draft Value</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {filteredPicks.map((rawPick) => {
                // eslint-disable-next-line @typescript-eslint/no-explicit-any
                const pick = rawPick as any;
                const hasPerformance = pick.actual_pts !== null && pick.actual_pts !== undefined;
                const delta = pick.value_delta ?? pick.delta ?? 0;
                const isSteal = hasPerformance && delta >= 10;
                const isReach = hasPerformance && delta <= -10;

                return (
                  <tr key={pick.pick_id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-3 px-4 text-center font-bold text-white">
                      #{pick.pick}
                    </td>
                    <td className="py-3 px-4 text-center text-slate-400">
                      R{pick.round}
                    </td>
                    <td className="py-3 px-4 font-bold text-white">
                      {pick.player_name}
                      {pick.is_keeper && (
                        <span className="ml-2 px-1.5 py-0.5 rounded text-[10px] font-extrabold bg-amber-500/20 text-amber-400 border border-amber-500/40 uppercase">
                          Keeper
                        </span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-center">
                      <span className={"px-2 py-0.5 rounded text-xs font-bold border " + getPositionBadge(pick.position)}>
                        {pick.position}
                      </span>
                    </td>
                    <td className="py-3 px-4 font-semibold text-slate-200">
                      {pick.manager_name}
                    </td>
                    <td className="py-3 px-4 text-xs italic text-slate-400">
                      {pick.team_name}
                    </td>
                    <td className="py-3 px-4 text-right font-medium">
                      {hasPerformance ? (
                        <div>
                          <span className="text-white font-bold">{pick.actual_pts.toFixed(1)}</span>
                          {pick.actual_rank && (
                            <span className="block text-[10px] text-slate-500 font-semibold">
                              Rank #{pick.actual_rank}
                            </span>
                          )}
                        </div>
                      ) : (
                        <span className="text-slate-600 text-xs">—</span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-right">
                      {hasPerformance ? (
                        isSteal ? (
                          <span className="px-2 py-0.5 rounded text-xs font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 whitespace-nowrap">
                            +{delta} Steal
                          </span>
                        ) : isReach ? (
                          <span className="px-2 py-0.5 rounded text-xs font-bold bg-rose-500/10 text-rose-400 border border-rose-500/30 whitespace-nowrap">
                            {delta} Reach
                          </span>
                        ) : (
                          <span className="text-xs text-slate-400 font-semibold">
                            {delta > 0 ? `+${delta}` : delta}
                          </span>
                        )
                      ) : (
                        <span className="text-slate-600 text-xs">Unranked</span>
                      )}
                    </td>
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
