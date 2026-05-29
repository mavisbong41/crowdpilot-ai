import { SeverityBadge, StatusBadge } from "../ui/Badge.jsx";

function formatTime(iso) {
  try {
    return new Date(iso).toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return iso;
  }
}

export default function IncidentsTable({ incidents }) {
  const activeCount = incidents.filter((i) => i.status !== "resolved" && i.status !== "closed").length;

  return (
    <section
      aria-labelledby="incidents-heading"
      className="overflow-hidden rounded-2xl border border-slate-800 bg-surface-900 shadow-lg"
    >
      <div className="flex items-center justify-between border-b border-slate-800 px-5 py-4">
        <div>
          <h2 id="incidents-heading" className="text-sm font-semibold tracking-wide text-white">
            Active Incidents
          </h2>
          <p className="text-xs text-slate-500">
            {activeCount} active · {incidents.length} total logged
          </p>
        </div>
        <button
          type="button"
          className="rounded-lg border border-slate-700 bg-surface-800 px-3 py-1.5 text-xs font-medium text-slate-300 transition hover:border-slate-600 hover:text-white"
        >
          Export CSV
        </button>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full min-w-[720px] text-left text-sm">
          <thead>
            <tr className="border-b border-slate-800/80 bg-surface-950/50 text-xs uppercase tracking-wider text-slate-500">
              <th className="px-5 py-3 font-medium">ID</th>
              <th className="px-5 py-3 font-medium">Location</th>
              <th className="px-5 py-3 font-medium">Severity</th>
              <th className="px-5 py-3 font-medium">Description</th>
              <th className="px-5 py-3 font-medium">Status</th>
              <th className="px-5 py-3 font-medium">Time</th>
              <th className="px-5 py-3 font-medium">Assignee</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {incidents.map((incident) => {
              const isResolved = incident.status === "resolved" || incident.status === "closed";
              return (
                <tr
                  key={incident.id}
                  className={`transition hover:bg-surface-800/40 ${isResolved ? "opacity-60" : ""}`}
                >
                  <td className="whitespace-nowrap px-5 py-3.5 font-mono text-xs text-accent-400">
                    {incident.id}
                  </td>
                  <td className="whitespace-nowrap px-5 py-3.5 font-medium text-white">{incident.location}</td>
                  <td className="px-5 py-3.5">
                    <SeverityBadge level={incident.severity} />
                  </td>
                  <td className="max-w-xs px-5 py-3.5 text-slate-400">{incident.description}</td>
                  <td className="px-5 py-3.5">
                    <StatusBadge status={incident.status} />
                  </td>
                  <td className="whitespace-nowrap px-5 py-3.5 font-mono text-xs text-slate-500">
                    {formatTime(incident.timestamp)}
                  </td>
                  <td className="whitespace-nowrap px-5 py-3.5 text-slate-400">{incident.assignee}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </section>
  );
}
