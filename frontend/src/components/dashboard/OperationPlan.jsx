import { IconClipboard } from "../icons.jsx";
import { RiskBadge } from "../ui/Badge.jsx";

function formatGenerated(iso) {
  try {
    return new Date(iso).toLocaleString("en-US", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return iso;
  }
}

export default function OperationPlan({ plan }) {
  return (
    <section
      aria-labelledby="plan-heading"
      className="flex h-full flex-col rounded-2xl border border-slate-800 bg-surface-900 shadow-lg"
    >
      <div className="flex items-center justify-between border-b border-slate-800 px-5 py-4">
        <div className="flex items-center gap-2">
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-violet-500/20 text-violet-300">
            <IconClipboard className="h-4 w-4" />
          </span>
          <div>
            <h2 id="plan-heading" className="text-sm font-semibold tracking-wide text-white">
              Operation Plan
            </h2>
            <p className="text-xs text-slate-500">Generated {formatGenerated(plan.generated_at)}</p>
          </div>
        </div>
        <RiskBadge level={plan.risk_level} />
      </div>

      <div className="flex-1 overflow-y-auto p-5">
        <p className="mb-4 text-xs font-medium uppercase tracking-wider text-slate-500">Recommendations</p>
        <ul className="space-y-3">
          {plan.recommendations.map((item, index) => (
            <li
              key={item}
              className="group flex gap-3 rounded-xl border border-slate-800/80 bg-surface-950/40 p-3.5 transition hover:border-violet-500/30 hover:bg-violet-500/5"
            >
              <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-violet-500/20 font-mono text-xs font-bold text-violet-300">
                {String(index + 1).padStart(2, "0")}
              </span>
              <p className="text-sm leading-relaxed text-slate-300 group-hover:text-slate-200">{item}</p>
            </li>
          ))}
        </ul>
      </div>

      <div className="border-t border-slate-800/80 px-5 py-3">
        <p className="text-center text-xs text-slate-500">
          Plans will sync from <span className="font-mono text-slate-400">/api/plans</span> when agents are connected
        </p>
      </div>
    </section>
  );
}
