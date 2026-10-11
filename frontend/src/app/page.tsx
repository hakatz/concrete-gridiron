"use client";

import { useState } from "react";
import Link from "next/link";
import leagueData from "@/data/league_analytics.json";
import { Trophy, Medal, Flame, Zap, Award, ArrowUpRight, TrendingUp, Shield, Activity, ChevronDown, ArrowUpDown } from "lucide-react";

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

export default function DashboardPage() {
  const { hall_of_fame, records, managers, historical_seasons } = leagueData;
  const [showRollCall, setShowRollCall] = useState(false);
  const [selectedSeason, setSelectedSeason] = useState<string>("ALL");
  const [sortField, setSortField] = useState<string>("win_pct");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");

  const titleCounts: Record<string, { count: number; name: string; id: string }> = {};
  hall_of_fame.forEach((hof) => {
    const id = hof.champion.manager_id;
    if (!titleCounts[id]) {
      titleCounts[id] = { count: 0, name: hof.champion.manager_name, id };
    }
    titleCounts[id].count += 1;
  });
  const sortedChamps = Object.values(titleCounts).sort((a, b) => b.count - a.count);

  const handleSort = (field: string) => {
    if (sortField === field) {
      setSortDir(sortDir === "desc" ? "asc" : "desc");
    } else {
      setSortField(field);
      setSortDir("desc");
    }
  };

  const handleSeasonChange = (val: string) => {
    setSelectedSeason(val);
    if (val !== "ALL") {
      setSortField("reg_finish");
      setSortDir("asc");
    } else {
      setSortField("win_pct");
      setSortDir("desc");
    }
  };

  const hofForSelectedYear = selectedSeason !== "ALL" 
    ? hall_of_fame.find((h) => h.year === Number(selectedSeason)) 
    : null;

  // Build rows based on Career (ALL) or Specific Season
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const tableRows: any[] = [];
  if (selectedSeason === "ALL") {
    managers.forEach((rawM: any) => {
      tableRows.push({
        id: rawM.manager_id,
        name: rawM.name,
        isChamp: false,
        isRunnerUp: false,
        playoffRank: null,
        titles: rawM.career.championships,
        wins: rawM.career.wins,
        losses: rawM.career.losses,
        ties: rawM.career.ties || 0,
        win_pct: rawM.career.win_pct,
        points_for: rawM.career.points_for,
        avg_pf: rawM.career.avg_pf_per_game,
        moves: rawM.career.total_moves,
        retention: rawM.career.roster_retention_rate || 0,
        archetypes: rawM.archetypes,
      });
    });
  } else {
    const yr = Number(selectedSeason);
    managers.forEach((rawM: any) => {
      const ht = (rawM.historical_teams || []).find((t: any) => t.year === yr);
      if (ht) {
        const isChamp = hofForSelectedYear?.champion?.manager_id === rawM.manager_id;
        const isRunnerUp = hofForSelectedYear?.runner_up?.manager_id === rawM.manager_id;
        const totalGames = ht.wins + ht.losses;
        const win_pct = totalGames > 0 ? Number(((ht.wins / totalGames) * 100).toFixed(1)) : 0;
        const avg_pf = totalGames > 0 ? Number((ht.pf / totalGames).toFixed(1)) : 0;
        tableRows.push({
          id: rawM.manager_id,
          name: rawM.name,
          teamName: ht.name,
          isChamp,
          isRunnerUp,
          playoffRank: ht.rank,
          titles: isChamp ? 1 : 0,
          wins: ht.wins,
          losses: ht.losses,
          ties: 0,
          win_pct,
          points_for: ht.pf,
          avg_pf,
          moves: ht.moves || 0,
          retention: 0,
          archetypes: rawM.archetypes,
        });
      }
    });

    // Compute regular season finish rank (seed by wins descending, then PF descending)
    tableRows.sort((a, b) => {
      if (b.wins !== a.wins) return b.wins - a.wins;
      return b.points_for - a.points_for;
    });
    tableRows.forEach((r, idx) => {
      r.reg_finish = idx + 1;
    });
  }

  // Apply user selected sorting
  tableRows.sort((a, b) => {
    let aVal = a[sortField];
    let bVal = b[sortField];
    if (aVal === undefined || aVal === null) aVal = 0;
    if (bVal === undefined || bVal === null) bVal = 0;
    if (typeof aVal === "string") {
      return sortDir === "asc" ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
    }
    return sortDir === "asc" ? aVal - bVal : bVal - aVal;
  });

  return (
    <div className="space-y-10">
      <div className="relative rounded-2xl bg-gradient-to-r from-slate-900 via-gridiron-900 to-slate-900 border border-slate-800 p-8 shadow-2xl overflow-hidden">
        <div className="absolute -right-10 -bottom-10 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold uppercase tracking-wider mb-3">
            <Shield className="w-3.5 h-3.5" />
            Verified Yahoo League #503435
          </div>
          <h1 className="text-3xl sm:text-4xl font-black text-white tracking-tight">
            THE CONCRETE GRIDIRON ARCHIVE
          </h1>
          <p className="mt-2 text-slate-400 text-sm sm:text-base max-w-3xl">
            12+ Seasons of fantasy football history ({historical_seasons[0]} – {historical_seasons[historical_seasons.length - 1]}). 
            Uncover historical manager tendencies, draft tendencies, waiver wire churn, and head-to-head rivalries.
          </p>
        </div>
      </div>

      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Trophy className="w-6 h-6 text-amber-400" />
            <h2 className="text-xl font-extrabold text-white tracking-tight">Hall of Champions & Trophy Case</h2>
          </div>
          <span className="text-xs font-semibold text-slate-400">All-Time Titles</span>
        </div>

        <div className="grid grid-cols-4 sm:grid-cols-8 gap-2">
          {sortedChamps.map((champ) => (
            <Link
              key={champ.id}
              href={`/managers/${champ.id}`}
              className="bg-slate-900/70 hover:bg-slate-800/80 border border-amber-500/20 hover:border-amber-500/50 rounded-lg p-2.5 transition-all group flex flex-col items-center text-center shadow-lg"
            >
              <div className="w-7 h-7 rounded-full bg-amber-500/10 border border-amber-500/30 flex items-center justify-center mb-1 group-hover:scale-110 transition-transform">
                <Trophy className="w-3.5 h-3.5 text-amber-400" />
              </div>
              <span className="text-xs font-bold text-white group-hover:text-amber-300 transition-colors truncate max-w-full">
                {champ.name}
              </span>
              <span className="text-[11px] font-extrabold text-amber-400 mt-0.5">
                {champ.count} {champ.count === 1 ? "Title" : "Titles"}
              </span>
            </Link>
          ))}
        </div>

        <div className="bg-slate-900/60 border border-slate-800 rounded-xl overflow-hidden shadow-xl">
          <button
            onClick={() => setShowRollCall(!showRollCall)}
            className="w-full px-6 py-4 border-b border-slate-800 flex items-center justify-between hover:bg-slate-800/40 transition-colors text-left cursor-pointer"
          >
            <div className="flex items-center gap-3">
              <h3 className="text-sm font-bold text-slate-300 uppercase tracking-wider">Championship Roll Call by Season</h3>
              <span className="text-xs text-slate-500">
                {historical_seasons[0]} – {historical_seasons[historical_seasons.length - 1]}
              </span>
            </div>
            <div className="flex items-center gap-2 text-xs font-semibold text-slate-400">
              <span>{showRollCall ? "Collapse" : "Expand"}</span>
              <ChevronDown className={`w-4 h-4 text-slate-400 transition-transform duration-200 ${showRollCall ? "rotate-180" : ""}`} />
            </div>
          </button>
          {showRollCall && (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="bg-slate-950/70 text-slate-400 uppercase text-xs border-b border-slate-800">
                  <tr>
                    <th className="py-3 px-4">Season</th>
                    <th className="py-3 px-4">Champion</th>
                    <th className="py-3 px-4">Champion Team</th>
                    <th className="py-3 px-4">Runner-Up</th>
                    <th className="py-3 px-4">Runner-Up Team</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 text-slate-300">
                  {hall_of_fame.map((hof) => (
                    <tr key={hof.year} className="hover:bg-slate-800/40 transition-colors">
                      <td className="py-3 px-4 font-black text-amber-400 flex items-center gap-2">
                        <Medal className="w-4 h-4 text-amber-400" />
                        {hof.year}
                      </td>
                      <td className="py-3 px-4 font-bold text-white">
                        <Link href={`/managers/${hof.champion.manager_id}`} className="hover:text-emerald-400 flex items-center gap-1">
                          {hof.champion.manager_name}
                          <ArrowUpRight className="w-3.5 h-3.5 opacity-60" />
                        </Link>
                      </td>
                      <td className="py-3 px-4 text-slate-400 italic">{hof.champion.team_name}</td>
                      <td className="py-3 px-4 text-slate-300">
                        {hof.runner_up ? (
                          <Link href={`/managers/${hof.runner_up.manager_id}`} className="hover:text-cyan-400">
                            {hof.runner_up.manager_name}
                          </Link>
                        ) : "—"}
                      </td>
                      <td className="py-3 px-4 text-slate-500 italic">{hof.runner_up?.team_name || "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </section>

      <section className="space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <Activity className="w-6 h-6 text-emerald-400" />
            <h2 className="text-xl font-extrabold text-white tracking-tight">
              {selectedSeason === "ALL" ? "All-Time Career Standings & Tendencies" : `${selectedSeason} Season Leaderboard`}
            </h2>
          </div>

          <div className="flex items-center gap-3">
            <span className="text-xs text-slate-400">Season:</span>
            <select
              value={selectedSeason}
              onChange={(e) => handleSeasonChange(e.target.value)}
              className="bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-xs font-bold text-white focus:outline-none focus:border-emerald-500 cursor-pointer"
            >
              <option value="ALL">All-Time Career</option>
              {historical_seasons.map((yr) => (
                <option key={yr} value={yr}>
                  {yr} Season
                </option>
              ))}
            </select>
            <span className="text-xs text-slate-500 hidden sm:inline">
              {selectedSeason === "ALL" ? "Sorted by Reg Win %" : "Sorted by Reg Finish"}
            </span>
          </div>
        </div>

        <div className="bg-slate-900/60 border border-slate-800 rounded-xl overflow-hidden shadow-xl">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-950/70 text-slate-400 uppercase text-xs border-b border-slate-800 select-none">
                <tr>
                  {selectedSeason !== "ALL" && (
                    <th
                      onClick={() => handleSort("reg_finish")}
                      className="py-3 px-4 text-center cursor-pointer hover:text-white transition-colors"
                    >
                      <div className="flex items-center justify-center gap-1">
                        Finish
                        <ArrowUpDown className="w-3 h-3 text-slate-500" />
                      </div>
                    </th>
                  )}
                  <th
                    onClick={() => handleSort("name")}
                    className="py-3 px-4 cursor-pointer hover:text-white transition-colors"
                  >
                    <div className="flex items-center gap-1">
                      Manager {selectedSeason !== "ALL" && "& Team"}
                      <ArrowUpDown className="w-3 h-3 text-slate-500" />
                    </div>
                  </th>
                  {selectedSeason === "ALL" ? (
                    <th
                      onClick={() => handleSort("titles")}
                      className="py-3 px-4 text-center cursor-pointer hover:text-white transition-colors"
                    >
                      <div className="flex items-center justify-center gap-1">
                        Titles
                        <ArrowUpDown className="w-3 h-3 text-slate-500" />
                      </div>
                    </th>
                  ) : (
                    <th
                      onClick={() => handleSort("playoffRank")}
                      className="py-3 px-4 text-center cursor-pointer hover:text-white transition-colors"
                    >
                      <div className="flex items-center justify-center gap-1">
                        Playoffs
                        <ArrowUpDown className="w-3 h-3 text-slate-500" />
                      </div>
                    </th>
                  )}
                  <th
                    onClick={() => handleSort("wins")}
                    className="py-3 px-4 text-center cursor-pointer hover:text-white transition-colors"
                  >
                    <div className="flex items-center justify-center gap-1">
                      Reg Record
                      <ArrowUpDown className="w-3 h-3 text-slate-500" />
                    </div>
                  </th>
                  <th
                    onClick={() => handleSort("win_pct")}
                    className="py-3 px-4 text-center cursor-pointer hover:text-white transition-colors"
                  >
                    <div className="flex items-center justify-center gap-1">
                      Reg Win %
                      <ArrowUpDown className="w-3 h-3 text-slate-500" />
                    </div>
                  </th>
                  <th
                    onClick={() => handleSort("points_for")}
                    className="py-3 px-4 text-right cursor-pointer hover:text-white transition-colors"
                  >
                    <div className="flex items-center justify-end gap-1">
                      Points For
                      <ArrowUpDown className="w-3 h-3 text-slate-500" />
                    </div>
                  </th>
                  <th
                    onClick={() => handleSort("avg_pf")}
                    className="py-3 px-4 text-right cursor-pointer hover:text-white transition-colors"
                  >
                    <div className="flex items-center justify-end gap-1">
                      Avg PF/G
                      <ArrowUpDown className="w-3 h-3 text-slate-500" />
                    </div>
                  </th>
                  <th
                    onClick={() => handleSort("moves")}
                    className="py-3 px-4 text-center cursor-pointer hover:text-white transition-colors"
                  >
                    <div className="flex items-center justify-center gap-1">
                      Moves
                      <ArrowUpDown className="w-3 h-3 text-slate-500" />
                    </div>
                  </th>
                  {selectedSeason === "ALL" && (
                    <th
                      onClick={() => handleSort("retention")}
                      className="py-3 px-4 text-center cursor-pointer hover:text-white transition-colors"
                    >
                      <div className="flex items-center justify-center gap-1">
                        Roster Retention
                        <ArrowUpDown className="w-3 h-3 text-slate-500" />
                      </div>
                    </th>
                  )}
                  <th className="py-3 px-4">Persona Archetype</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300">
                {tableRows.map((r: any) => {
                  let rowHighlight = "hover:bg-slate-800/40";
                  if (selectedSeason !== "ALL") {
                    if (r.isChamp) {
                      rowHighlight = "bg-amber-500/10 hover:bg-amber-500/20 border-l-4 border-l-amber-400";
                    } else if (r.isRunnerUp) {
                      rowHighlight = "bg-slate-400/10 hover:bg-slate-400/20 border-l-4 border-l-slate-300";
                    }
                  }

                  return (
                    <tr key={r.id} className={`transition-colors ${rowHighlight}`}>
                      {selectedSeason !== "ALL" && (
                        <td className="py-3 px-4 text-center font-bold text-slate-400">
                          #{r.reg_finish}
                        </td>
                      )}
                      <td className="py-3 px-4">
                        <Link href={`/managers/${r.id}`} className="font-bold text-white hover:text-emerald-400 inline-flex items-center gap-2">
                          {r.name}
                          <ArrowUpRight className="w-3.5 h-3.5 text-slate-500" />
                        </Link>
                        {selectedSeason !== "ALL" && r.teamName && (
                          <span className="block text-xs text-slate-400 italic truncate max-w-[200px]">
                            {r.teamName}
                          </span>
                        )}
                      </td>
                      {selectedSeason === "ALL" ? (
                        <td className="py-3 px-4 text-center font-extrabold text-amber-400">
                          {r.titles > 0 ? `🏆 ${r.titles}` : "—"}
                        </td>
                      ) : (
                        <td className="py-3 px-4 text-center font-bold">
                          {r.isChamp ? (
                            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-amber-400/20 border border-amber-400/40 text-amber-300 text-xs font-black">
                              <Trophy className="w-3 h-3 text-amber-400" /> 1st (Gold)
                            </span>
                          ) : r.isRunnerUp ? (
                            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-slate-300/20 border border-slate-300/40 text-slate-200 text-xs font-bold">
                              <Medal className="w-3 h-3 text-slate-300" /> 2nd (Silver)
                            </span>
                          ) : r.playoffRank ? (
                            <span className="text-xs text-slate-400">{r.playoffRank}th</span>
                          ) : (
                            <span className="text-xs text-slate-500">—</span>
                          )}
                        </td>
                      )}
                      <td className="py-3 px-4 text-center font-semibold text-slate-200">
                        {r.wins}-{r.losses}{r.ties > 0 ? `-${r.ties}` : ""}
                      </td>
                      <td className="py-3 px-4 text-center font-bold text-emerald-400">
                        {r.win_pct}%
                      </td>
                      <td className="py-3 px-4 text-right text-slate-300">
                        {r.points_for.toLocaleString()}
                      </td>
                      <td className="py-3 px-4 text-right font-medium text-cyan-400">
                        {r.avg_pf}
                      </td>
                      <td className="py-3 px-4 text-center text-slate-400">
                        {r.moves}
                      </td>
                      {selectedSeason === "ALL" && (
                        <td className="py-3 px-4 text-center text-purple-400 font-semibold">
                          {r.retention ? `${r.retention}%` : "—"}
                        </td>
                      )}
                      <td className="py-3 px-4">
                        <div className="flex flex-wrap gap-1">
                          {r.archetypes.slice(0, 2).map((arch: string) => (
                            <span
                              key={arch}
                              title={ARCHETYPE_DESCRIPTIONS[arch] || arch}
                              className="px-2 py-0.5 rounded-full text-xs font-semibold bg-slate-800 text-slate-300 border border-slate-700 cursor-help"
                            >
                              {arch}
                            </span>
                          ))}
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <section className="space-y-4">
        <div className="flex items-center gap-2">
          <Flame className="w-6 h-6 text-rose-500" />
          <h2 className="text-xl font-extrabold text-white tracking-tight">League Record Book</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 shadow-xl">
            <h3 className="text-sm font-bold text-emerald-400 uppercase tracking-wider mb-3 flex items-center gap-1.5">
              <Zap className="w-4 h-4" /> All-Time High Scores
            </h3>
            <div className="space-y-2.5">
              {records.all_time_high_scores.slice(0, 5).map((r, i) => (
                <div key={i} className="flex items-center justify-between text-xs py-1 border-b border-slate-800/60 last:border-0">
                  <div>
                    <p className="font-bold text-white">{r.manager_name}</p>
                    <p className="text-slate-500">Yr {r.year}, Wk {r.week}</p>
                  </div>
                  <span className="font-black text-emerald-400 text-sm">{r.score.toFixed(2)}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 shadow-xl">
            <h3 className="text-sm font-bold text-rose-400 uppercase tracking-wider mb-3 flex items-center gap-1.5">
              <TrendingUp className="w-4 h-4 rotate-180" /> All-Time Low Scores
            </h3>
            <div className="space-y-2.5">
              {records.all_time_low_scores.slice(0, 5).map((r, i) => (
                <div key={i} className="flex items-center justify-between text-xs py-1 border-b border-slate-800/60 last:border-0">
                  <div>
                    <p className="font-bold text-white">{r.manager_name}</p>
                    <p className="text-slate-500">Yr {r.year}, Wk {r.week}</p>
                  </div>
                  <span className="font-black text-rose-400 text-sm">{r.score.toFixed(2)}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 shadow-xl">
            <h3 className="text-sm font-bold text-amber-400 uppercase tracking-wider mb-3 flex items-center gap-1.5">
              <Flame className="w-4 h-4" /> Biggest Blowouts
            </h3>
            <div className="space-y-2.5">
              {records.biggest_blowouts.slice(0, 5).map((r, i) => (
                <div key={i} className="flex items-center justify-between text-xs py-1 border-b border-slate-800/60 last:border-0">
                  <div>
                    <p className="font-bold text-white">{r.manager_name} vs {r.opponent_name}</p>
                    <p className="text-slate-500">Yr {r.year}, Wk {r.week}</p>
                  </div>
                  <span className="font-black text-amber-400 text-sm">+{r.margin.toFixed(2)}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 shadow-xl">
            <h3 className="text-sm font-bold text-cyan-400 uppercase tracking-wider mb-3 flex items-center gap-1.5">
              <Award className="w-4 h-4" /> Closest Nail-Biters
            </h3>
            <div className="space-y-2.5">
              {records.closest_games.slice(0, 5).map((r, i) => (
                <div key={i} className="flex items-center justify-between text-xs py-1 border-b border-slate-800/60 last:border-0">
                  <div>
                    <p className="font-bold text-white">{r.manager_name} vs {r.opponent_name}</p>
                    <p className="text-slate-500">Yr {r.year}, Wk {r.week}</p>
                  </div>
                  <span className="font-black text-cyan-400 text-sm">Δ {r.margin.toFixed(2)}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
