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
