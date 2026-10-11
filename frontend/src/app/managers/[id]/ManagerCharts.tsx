"use client";

import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
} from "recharts";
import { Sparkles, Layers } from "lucide-react";

interface ManagerChartsProps {
  managerName: string;
  radarData: Array<{ subject: string; value: number; fullMark: number }>;
  barData: Array<{ phase: string; RB: number; WR: number; QB: number; TE: number }>;
}

export default function ManagerCharts({ managerName, radarData, barData }: ManagerChartsProps) {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div className="rounded-xl bg-slate-900/60 border border-slate-800 p-6 shadow-xl space-y-4">
        <div>
          <h3 className="text-base font-bold text-white tracking-tight flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-emerald-400" /> Manager Tendency Radar
          </h3>
          <p className="text-xs text-slate-400">
            Relative style index across drafting, streaming &amp; churn (0-100 scale)
          </p>
        </div>
        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <RadarChart data={radarData}>
              <PolarGrid stroke="#334155" />
              <PolarAngleAxis dataKey="subject" tick={{ fill: "#94a3b8", fontSize: 11 }} />
              <Radar
                name={managerName}
                dataKey="value"
                stroke="#10b981"
                fill="#10b981"
                fillOpacity={0.35}
              />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="rounded-xl bg-slate-900/60 border border-slate-800 p-6 shadow-xl space-y-4">
        <div>
          <h3 className="text-base font-bold text-white tracking-tight flex items-center gap-2">
            <Layers className="w-4 h-4 text-cyan-400" /> Draft Phase Allocation
          </h3>
          <p className="text-xs text-slate-400">
            Positions targeted across Early (1-3), Mid (4-7), and Late (8+) rounds
          </p>
        </div>
        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={barData}>
              <XAxis dataKey="phase" stroke="#64748b" fontSize={12} />
              <YAxis stroke="#64748b" fontSize={12} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#0f172a",
                  borderColor: "#334155",
                  borderRadius: "8px",
                }}
              />
              <Legend wrapperStyle={{ fontSize: "11px" }} />
              <Bar dataKey="RB" stackId="a" fill="#10b981" />
              <Bar dataKey="WR" stackId="a" fill="#3b82f6" />
              <Bar dataKey="QB" stackId="a" fill="#f59e0b" />
              <Bar dataKey="TE" stackId="a" fill="#8b5cf6" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
