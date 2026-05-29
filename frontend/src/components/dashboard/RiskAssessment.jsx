import { IconAlert } from "../icons.jsx";
import { RiskBadge } from "../ui/Badge.jsx";

const RISK_THEME = {
  low: {
    ring: "ring-emerald-500/40",
    glow: "from-emerald-500/30",
    bar: "bg-emerald-500",
    text: "text-emerald-300",
  },
  medium: {
    ring: "ring-amber-500/40",
    glow: "from-amber-500/30",
    bar: "bg-amber-500",
    text: "text-amber-300",
  },
  high: {
    ring: "ring-orange-500/40",
    glow: "from-orange-500/30",
    bar: "bg-orange-500",
    text: "text-orange-300",
  },
  critical: {
    ring: "ring-rose-500/40",
    glow: "from-rose-500/30",
    bar: "bg-rose-500",
    text: "text-rose-300",
  },
};

function TrendIcon({ trend }) {
  if (trend === "up") {
    return <span className="text-rose-400">↑</span>;
  }
  if (trend === "ok") {
    return <span className="text-emerald-400">✓</span>;
  }
  return <span className="text-slate-500">→</span>;
}

export default function RiskAssessment({ risk }) {
  const theme = RISK_THEME[risk.risk_level] ?? RISK_THEME.medium;

  return (
    <section
      aria-labelledby="risk-heading"
      className="flex h-full flex-col overflow-hidden rounded-2xl border border-slate-800 bg-surface-900 shadow-lg"
    >
      <div className="flex items-center justify-between border-b border-slate-800 px-5 py-4">
        <div className="flex items-center gap-2">
          <span className={`flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br ${theme.glow} to-transparent ${theme.text}`}>
            <IconAlert className="h-4 w-4" />
          </span>
          <div>
            <h2 id="risk-heading" className="text-sm font-semibold tracking-wide text-white">
              Risk Assessment
            </h2>
            <p className="text-xs text-slate-500">Real-time crowd surge analysis</p>
          </div>
        </div>
        <RiskBadge level={risk.risk_level} />
      </div>

      <div className="flex flex-1 flex-col gap-5 p-5">
        <div className={`relative overflow-hidden rounded-2xl bg-surface-800/80 p-6 ring-1 ring-inset ${theme.ring}`}>
          <div className={`absolute inset-0 bg-gradient-to-br ${theme.glow} to-transparent opacity-40`} />
          <div className="relative flex flex-col items-center text-center sm:flex-row sm:items-end sm:justify-between sm:text-left">
            <div>
              <p className="text-xs font-medium uppercase tracking-wider text-slate-400">Risk level</p>
              <p className={`mt-1 text-4xl font-bold capitalize ${theme.text}`}>{risk.risk_level}</p>
              <p className="mt-2 max-w-sm text-sm text-slate-400">{risk.summary}</p>
            </div>
            <div className="mt-4 sm:mt-0 sm:text-right">
              <p className="text-xs text-slate-500">Risk score</p>
              <p className="font-mono text-5xl font-bold text-white">{risk.score}</p>
              <p className="mt-1 text-xs text-slate-500">
                Surge probability: <span className="font-medium text-white">{(risk.surge_probability * 100).toFixed(0)}%</span>
              </p>
            </div>
          </div>

          <div className="relative mt-6">
            <div className="mb-1 flex justify-between text-xs text-slate-500">
              <span>Low</span>
              <span>Critical</span>
            </div>
            <div className="h-2 overflow-hidden rounded-full bg-slate-900">
              <div className={`h-full rounded-full ${theme.bar}`} style={{ width: `${risk.score}%` }} />
            </div>
            <p className="mt-2 text-center text-xs text-slate-500 sm:text-left">
              Peak window: <span className="font-medium text-slate-300">{risk.peak_window}</span>
            </p>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-2">
          {risk.factors.map((factor) => (
            <div
              key={factor.label}
              className="flex items-center justify-between rounded-xl border border-slate-800/80 bg-surface-950/50 px-3 py-2.5"
            >
              <div>
                <p className="text-[10px] uppercase tracking-wider text-slate-500">{factor.label}</p>
                <p className="text-sm font-semibold text-white">{factor.value}</p>
              </div>
              <TrendIcon trend={factor.trend} />
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
