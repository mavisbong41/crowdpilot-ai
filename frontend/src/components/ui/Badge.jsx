const SEVERITY_STYLES = {
  low: "bg-emerald-500/15 text-emerald-300 ring-emerald-500/30",
  medium: "bg-amber-500/15 text-amber-300 ring-amber-500/30",
  high: "bg-orange-500/15 text-orange-300 ring-orange-500/30",
  critical: "bg-rose-500/15 text-rose-300 ring-rose-500/30",
};

const STATUS_STYLES = {
  open: "bg-slate-500/15 text-slate-300 ring-slate-500/30",
  acknowledged: "bg-sky-500/15 text-sky-300 ring-sky-500/30",
  in_progress: "bg-violet-500/15 text-violet-300 ring-violet-500/30",
  resolved: "bg-emerald-500/15 text-emerald-300 ring-emerald-500/30",
  closed: "bg-slate-600/15 text-slate-400 ring-slate-600/30",
};

export function SeverityBadge({ level }) {
  const style = SEVERITY_STYLES[level] ?? SEVERITY_STYLES.medium;
  return (
    <span className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium capitalize ring-1 ring-inset ${style}`}>
      {level}
    </span>
  );
}

export function StatusBadge({ status }) {
  const style = STATUS_STYLES[status] ?? STATUS_STYLES.open;
  const label = status.replace(/_/g, " ");
  return (
    <span className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium capitalize ring-1 ring-inset ${style}`}>
      {label}
    </span>
  );
}

export function RiskBadge({ level }) {
  return <SeverityBadge level={level} />;
}
