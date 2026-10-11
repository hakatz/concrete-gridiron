code = """import Link from "next/link";
import leagueData from "@/data/league_analytics.json";
import { Trophy, Medal, Flame, Zap, Award, ArrowUpRight, TrendingUp, Shield, Activity } from "lucide-react";

export default function DashboardPage() {
  const { hall_of_fame, records, managers, historical_seasons, active_year } = leagueData;

  const titleCounts: Record<string, { count: number; name: string; id: string }> = {};
  hall_of_fame.forEach((hof) => {
    const id = hof.champion.manager_id;
    if (!titleCounts[id]) {
      titleCounts[id] = { count: 0, name: hof.champion.manager_name, id };
    }
    titleCounts[id].count += 1;
  });
  const sortedChamps = Object.values(titleCounts).sort((a, b) => b.count - a.count);

  return (
    <div className="space-y-10">
      <div className="relative rounded-2xl bg-gradient-to-r from-slate-900 via-gridiron-900 to-slate-900 border border-slate-800 p-8 shadow-2xl overflow-hidden">
        <div className="absolute -right-10 -bottom-10 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold uppercase tracking-wider mb-3">
              <Shield className="w-3.5 h-3.5" />
              Verified Yahoo League #503435
            </div>
            <h1 className="text-3xl sm:text-4xl font-black text-white tracking-tight">
              THE CONCRETE GRIDIRON ARCHIVE
            </h1>
            <p className="mt-2 text-slate-400 text-sm sm:text-base max-w-2xl">
              12+ Seasons of fantasy football history ({historical_seasons[0]} – {historical_seasons[historical_seasons.length - 1]}). 
              Uncover historical manager tendencies, draft tendencies, waiver wire churn, and head-to-head rivalries.
            </p>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-3 text-center">
              <span className="text-xs text-slate-500 uppercase font-semibold">Seasons</span>
              <p className="text-2xl font-black text-emerald-400">{historical_seasons.length}</p>
            </div>
            <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-3 text-center">
              <span className="text-xs text-slate-500 uppercase font-semibold">Managers</span>
              <p className="text-2xl font-black text-amber-400">{managers.length}</p>
            </div>
            <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-3 text-center">
              <span className="text-xs text-slate-500 uppercase font-semibold">Active Year</span>
              <p className="text-2xl font-black text-cyan-400">{active_year}</p>
            </div>
            <div className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-3 text-center">
              <span className="text-xs text-slate-500 uppercase font-semibold">Champions</span>
              <p className="text-2xl font-black text-purple-400">{sortedChamps.length}</p>
            </div>
          </div>
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

        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-3">
          {sortedChamps.map((champ) => (
            <Link
              key={champ.id}
              href={`/managers/${champ.id}`}
              className="bg-slate-900/70 hover:bg-slate-800/80 border border-amber-500/20 hover:border-amber-500/50 rounded-xl p-4 transition-all group flex flex-col items-center text-center shadow-lg"
            >
              <div className="w-10 h-10 rounded-full bg-amber-500/10 border border-amber-500/30 flex items-center justify-center mb-2 group-hover:scale-110 transition-transform">
                <Trophy className="w-5 h-5 text-amber-400" />
              </div>
              <span className="text-sm font-bold text-white group-hover:text-amber-300 transition-colors truncate max-w-full">
                {champ.name}
              </span>
              <span className="text-xs font-extrabold text-amber-400 mt-1">
                {champ.count} {champ.count === 1 ? "Title" : "Titles"}
              </span>
            </Link>
          ))}
        </div>

        <div className="bg-slate-900/60 border border-slate-800 rounded-xl overflow-hidden shadow-xl">
          <div className="px-6 py-4 border-b border-slate-800 flex items-center justify-between">
            <h3 className="text-sm font-bold text-slate-300 uppercase tracking-wider">Championship Roll Call by Season</h3>
            <span className="text-xs text-slate-500">2014 – 2025</span>
          </div>
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
        </div>
      </section>

      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Activity className="w-6 h-6 text-emerald-400" />
            <h2 className="text-xl font-extrabold text-white tracking-tight">All-Time Career Standings & Tendencies</h2>
          </div>
          <span className="text-xs text-slate-400">Sorted by Championships & Win %</span>
        </div>

        <div className="bg-slate-900/60 border border-slate-800 rounded-xl overflow-hidden shadow-xl">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-950/70 text-slate-400 uppercase text-xs border-b border-slate-800">
                <tr>
                  <th className="py-3 px-4">Manager</th>
                  <th className="py-3 px-4 text-center">Titles</th>
                  <th className="py-3 px-4 text-center">W-L-T</th>
                  <th className="py-3 px-4 text-center">Win %</th>
                  <th className="py-3 px-4 text-right">Points For</th>
                  <th className="py-3 px-4 text-right">Avg PF/G</th>
                  <th className="py-3 px-4 text-center">Moves</th>
                  <th className="py-3 px-4 text-center">Roster Retention</th>
                  <th className="py-3 px-4">Persona Archetype</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300">
                {managers.map((m) => (
                  <tr key={m.manager_id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-3 px-4">
                      <Link href={`/managers/${m.manager_id}`} className="font-bold text-white hover:text-emerald-400 flex items-center gap-2">
                        {m.name}
                        <ArrowUpRight className="w-3.5 h-3.5 text-slate-500" />
                      </Link>
                    </td>
                    <td className="py-3 px-4 text-center font-extrabold text-amber-400">
                      {m.career.championships > 0 ? "🏆 " + m.career.championships : "—"}
                    </td>
                    <td className="py-3 px-4 text-center font-semibold text-slate-200">
                      {m.career.wins}-{m.career.losses}{m.career.ties > 0 ? "-" + m.career.ties : ""}
                    </td>
                    <td className="py-3 px-4 text-center font-bold text-emerald-400">
                      {m.career.win_pct}%
                    </td>
                    <td className="py-3 px-4 text-right text-slate-300">
                      {m.career.points_for.toLocaleString()}
                    </td>
                    <td className="py-3 px-4 text-right font-medium text-cyan-400">
                      {m.career.avg_pf_per_game}
                    </td>
                    <td className="py-3 px-4 text-center text-slate-400">
                      {m.career.total_moves}
                    </td>
                    <td className="py-3 px-4 text-center text-purple-400 font-semibold">
                      {m.career.roster_retention_rate ? m.career.roster_retention_rate + "%" : "—"}
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex flex-wrap gap-1">
                        {m.archetypes.slice(0, 2).map((arch: string) => (
                          <span
                            key={arch}
                            className="px-2 py-0.5 rounded-full text-xs font-semibold bg-slate-800 text-slate-300 border border-slate-700"
                          >
                            {arch}
                          </span>
                        ))}
                      </div>
                    </td>
                  </tr>
                ))}
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
"""

with open("frontend/src/app/page.tsx", "w", encoding="utf-8") as f:
    f.write(code)
print("Updated page.tsx")
