export default function StatCard({ icon: Icon, label, value, subtext, accent = "sky" }) {
  const accents = {
    sky: "from-sky-500/20 to-sky-500/5 text-sky-400",
    violet: "from-violet-500/20 to-violet-500/5 text-violet-400",
    emerald: "from-emerald-500/20 to-emerald-500/5 text-emerald-400",
    amber: "from-amber-500/20 to-amber-500/5 text-amber-400",
  };

  return (
    <div className="group relative overflow-hidden rounded-2xl border border-slate-800 bg-surface-900 p-5 shadow-lg transition hover:border-slate-700">
      <div className={`absolute -right-4 -top-4 h-24 w-24 rounded-full bg-gradient-to-br ${accents[accent]} opacity-60 blur-2xl transition group-hover:opacity-100`} />
      <div className="relative">
        <div className="mb-3 flex items-center gap-2">
          {Icon && (
            <span className={`flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br ${accents[accent]} ring-1 ring-white/5`}>
              <Icon className="h-4 w-4" />
            </span>
          )}
          <p className="text-xs font-medium uppercase tracking-wider text-slate-500">{label}</p>
        </div>
        <p className="text-2xl font-bold tracking-tight text-white sm:text-3xl">{value}</p>
        {subtext && <p className="mt-1.5 text-sm text-slate-400">{subtext}</p>}
      </div>
    </div>
  );
}
