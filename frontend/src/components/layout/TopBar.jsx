import { IconRadar } from "../icons.jsx";

function LiveClock() {
  const now = new Date();
  const time = now.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" });
  const date = now.toLocaleDateString("en-US", { weekday: "short", month: "short", day: "numeric" });

  return (
    <div className="hidden text-right sm:block">
      <p className="font-mono text-sm font-medium text-white">{time}</p>
      <p className="text-xs text-slate-500">{date}</p>
    </div>
  );
}

export default function TopBar({ event }) {
  return (
    <header className="sticky top-0 z-40 border-b border-slate-800/80 bg-surface-950/80 backdrop-blur-xl">
      <div className="mx-auto flex max-w-[1600px] flex-wrap items-center justify-between gap-4 px-4 py-3 sm:px-6 lg:px-8">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-accent-500 to-indigo-600 shadow-lg shadow-sky-500/25">
            <IconRadar className="h-5 w-5 text-white" />
          </div>
          <div>
            <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-accent-400">
              Google Cloud Rapid Agent Hackathon
            </p>
            <h1 className="text-lg font-bold text-white sm:text-xl">CrowdPilot AI</h1>
          </div>
        </div>

        <div className="flex flex-1 flex-wrap items-center justify-end gap-3 sm:gap-4">
          <div className="hidden items-center gap-2 rounded-full border border-slate-800 bg-surface-900/80 px-3 py-1.5 md:flex">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-60" />
              <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-400" />
            </span>
            <span className="text-xs font-medium text-slate-300">Live monitoring</span>
          </div>

          <div className="rounded-full border border-amber-500/30 bg-amber-500/10 px-3 py-1 text-xs font-medium text-amber-200">
            Mock data
          </div>

          <LiveClock />
        </div>
      </div>

      <div className="border-t border-slate-800/60 bg-surface-900/50">
        <div className="mx-auto flex max-w-[1600px] flex-wrap items-center gap-x-6 gap-y-1 px-4 py-2 text-sm sm:px-6 lg:px-8">
          <span className="font-medium text-white">{event.event_name}</span>
          <span className="hidden text-slate-600 sm:inline">|</span>
          <span className="text-slate-400">{event.venue}</span>
          <span className="hidden text-slate-600 md:inline">|</span>
          <span className="hidden text-slate-400 md:inline">
            {event.event_date} · {event.event_time}
          </span>
        </div>
      </div>
    </header>
  );
}
