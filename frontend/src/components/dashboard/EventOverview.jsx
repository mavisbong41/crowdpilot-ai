import { IconBuilding, IconUsers } from "../icons.jsx";
import StatCard from "../ui/StatCard.jsx";

function CapacityBar({ forecast, capacity, event }) {
  const utilization = Math.min(100, Math.round((forecast / capacity) * 100));
  const isOver = forecast > capacity;

  return (
    <div className="rounded-2xl border border-slate-800 bg-surface-900 p-5 shadow-lg">
      <div className="mb-4 flex flex-wrap items-end justify-between gap-2">
        <div>
          <h2 className="text-sm font-semibold tracking-wide text-white">Capacity utilization</h2>
          <p className="mt-0.5 text-xs text-slate-500">Forecast vs. venue limit</p>
        </div>
        <div className="text-right">
          <p className={`text-2xl font-bold ${isOver ? "text-rose-400" : "text-white"}`}>{utilization}%</p>
          {isOver && (
            <p className="text-xs font-medium text-rose-400">
              +{(forecast - capacity).toLocaleString()} over capacity
            </p>
          )}
        </div>
      </div>

      <div className="relative h-4 overflow-hidden rounded-full bg-slate-800">
        <div
          className={`absolute inset-y-0 left-0 rounded-full transition-all ${
            isOver
              ? "bg-gradient-to-r from-amber-500 via-orange-500 to-rose-500"
              : "bg-gradient-to-r from-accent-600 to-emerald-500"
          }`}
          style={{ width: `${Math.min(utilization, 100)}%` }}
        />
        {isOver && (
          <div
            className="absolute inset-y-0 rounded-full bg-rose-500/40"
            style={{ left: "100%", width: `${utilization - 100}%`, transform: "translateX(-100%)" }}
          />
        )}
      </div>

      <div className="mt-3 flex justify-between text-xs text-slate-500">
        <span>0</span>
        <span>Capacity: {capacity.toLocaleString()}</span>
      </div>

      <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-4">
        <div className="rounded-xl bg-surface-800/60 px-3 py-2">
          <p className="text-[10px] uppercase tracking-wider text-slate-500">Expected</p>
          <p className="font-semibold text-white">{event.expected_attendance.toLocaleString()}</p>
        </div>
        <div className="rounded-xl bg-surface-800/60 px-3 py-2">
          <p className="text-[10px] uppercase tracking-wider text-slate-500">Forecast peak</p>
          <p className="font-semibold text-amber-300">{forecast.toLocaleString()}</p>
        </div>
        <div className="rounded-xl bg-surface-800/60 px-3 py-2">
          <p className="text-[10px] uppercase tracking-wider text-slate-500">Weather</p>
          <p className="font-semibold text-white">{event.weather.condition}</p>
        </div>
        <div className="rounded-xl bg-surface-800/60 px-3 py-2">
          <p className="text-[10px] uppercase tracking-wider text-slate-500">Temp</p>
          <p className="font-semibold text-white">{event.weather.temperature_c}°C</p>
        </div>
      </div>
    </div>
  );
}

export default function EventOverview({ event }) {
  const forecastDelta =
    event.forecast_delta_percent > 0
      ? `+${event.forecast_delta_percent}% vs. expected`
      : `${event.forecast_delta_percent}% vs. expected`;

  return (
    <section aria-labelledby="event-overview-heading">
      <div className="mb-4 flex items-center gap-2">
        <h2 id="event-overview-heading" className="text-base font-semibold text-white">
          Event Overview
        </h2>
        <span className="rounded-md bg-surface-800 px-2 py-0.5 text-[10px] font-medium uppercase tracking-wider text-slate-400">
          Section 1
        </span>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <StatCard
          icon={IconUsers}
          label="Event name"
          value={event.event_name.split("—")[0].trim()}
          subtext={event.event_name.includes("—") ? event.event_name.split("—")[1].trim() : event.venue}
          accent="sky"
        />
        <StatCard
          icon={IconUsers}
          label="Attendance forecast"
          value={event.attendance_forecast.toLocaleString()}
          subtext={forecastDelta}
          accent="amber"
        />
        <StatCard
          icon={IconBuilding}
          label="Venue capacity"
          value={event.venue_capacity.toLocaleString()}
          subtext={`${event.venue} · ${event.expected_attendance.toLocaleString()} expected`}
          accent="emerald"
        />
      </div>
      <div className="mt-4">
        <CapacityBar forecast={event.attendance_forecast} capacity={event.venue_capacity} event={event} />
      </div>
    </section>
  );
}
