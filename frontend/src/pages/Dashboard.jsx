import { useMemo, useState } from "react";
import { api } from "../api/client.js";
import {
  IconActivity,
  IconAlert,
  IconBuilding,
  IconCheck,
  IconDatabase,
  IconPlay,
  IconRadar,
  IconRoute,
  IconUsers,
} from "../components/icons.jsx";

const initialMission = {
  event_name: "World Cup 2026 Fan Zone - Downtown Plaza",
  venue: "Downtown Plaza, Gate A/B corridor",
  mission_goal:
    "Prevent entry bottlenecks, keep medical response under 8 minutes, and generate an operator-approved crowd plan before the evening surge.",
  expected_attendance: 42500,
  venue_capacity: 50000,
  weather_condition: "Humid, 31C, light wind",
  time_window: "18:00-22:30",
  incident_data: [
    {
      id: "INC-1042",
      location: "Gate A main ingress",
      severity: "high",
      description: "Queue depth exceeds 400m and wait time is trending above 35 minutes.",
      status: "open",
    },
    {
      id: "INC-1041",
      location: "Stage Front Zone 2",
      severity: "medium",
      description: "Density approaching 4.5 persons per square meter near the sponsor stage.",
      status: "in_progress",
    },
    {
      id: "INC-1039",
      location: "East medical tent",
      severity: "low",
      description: "Heat-related assistance requests are 18% above baseline.",
      status: "open",
    },
  ],
};

const fallbackResult = {
  agents: {
    forecast: {
      crowd_risk_level: "high",
      utilization_ratio: 0.85,
      congestion_zones: [
        { zone: "Gate A", level: "critical", reason: "Queue depth and ingress rate exceed safe flow." },
        { zone: "Stage Front Zone 2", level: "high", reason: "Static crowd density is rising near stage." },
        { zone: "Transit Exit", level: "moderate", reason: "Departure wave expected after final whistle." },
      ],
    },
    resources: {
      recommended_security_staff: 92,
      recommended_traffic_controllers: 28,
      recommended_medical_staff: 18,
    },
    incidents: {
      response_actions: [
        {
          incident_ref: "INC-1042",
          location: "Gate A main ingress",
          priority: "high",
          action: "Open auxiliary lanes, throttle scans, and deploy supervisors to the queue terminus.",
        },
        {
          incident_ref: "INC-1041",
          location: "Stage Front Zone 2",
          priority: "medium",
          action: "Create a lateral release path and move roaming staff to the sponsor stage edge.",
        },
      ],
    },
  },
  operation_plan: {
    risk_level: "high",
    mission_summary:
      "CrowdPilot planned a supervised multi-step response for World Cup 2026 Fan Zone using MongoDB partner tools as operational memory.",
    recommendations: [
      "Maintain HIGH posture for the fan zone with hourly operator review.",
      "Open Gate C overflow lanes before the 18:30 arrival wave.",
      "Deploy 92 security staff, 28 traffic controllers, and 18 medical staff.",
      "[Gate A main ingress] Open auxiliary lanes and dispatch queue supervisors.",
      "[Stage Front Zone 2] Create a lateral release path and rebalance roaming staff.",
    ],
    execution_steps: [
      "Read event profile, active incidents, and prior plans from MongoDB.",
      "Forecast utilization and identify congestion zones.",
      "Calculate staffing levels from risk, capacity, and active incident severity.",
      "Convert incidents into prioritized field actions.",
      "Persist the plan for supervisor approval and demo replay.",
    ],
    success_metrics: [
      "Supervisor can approve or edit the plan before field dispatch.",
      "Keep venue utilization below 92% during 18:00-22:30.",
      "Reduce high-severity incident response time to under 8 minutes.",
      "Maintain a complete MongoDB audit trail for event, incident, and plan updates.",
    ],
    partner_tool_calls: [
      {
        partner: "MongoDB",
        mcp_server: "mongodb/mongodb-mcp-server",
        tool: "find",
        collection: "events, incidents",
        status: "executed",
        purpose: "Load event profile and active incidents for the coordinator mission.",
      },
      {
        partner: "MongoDB",
        mcp_server: "mongodb/mongodb-mcp-server",
        tool: "aggregate",
        collection: "events",
        status: "executed",
        purpose: "Compare attendance, capacity, and incident severity signals.",
      },
      {
        partner: "MongoDB",
        mcp_server: "mongodb/mongodb-mcp-server",
        tool: "insertOne",
        collection: "operation_plans",
        status: "planned",
        purpose: "Save generated operation plan for human approval and demo replay.",
      },
    ],
    generated_at: new Date().toISOString(),
  },
};

const riskColors = {
  low: "text-emerald-700 bg-emerald-50 border-emerald-200",
  medium: "text-amber-700 bg-amber-50 border-amber-200",
  high: "text-orange-700 bg-orange-50 border-orange-200",
  critical: "text-rose-700 bg-rose-50 border-rose-200",
};

function Field({ label, children }) {
  return (
    <label className="block">
      <span className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500">{label}</span>
      {children}
    </label>
  );
}

function inputClass() {
  return "w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 outline-none transition focus:border-teal-500 focus:ring-2 focus:ring-teal-500/20";
}

function Metric({ icon: Icon, label, value, detail }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
      <div className="flex items-start gap-3">
        <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-slate-100 text-slate-700">
          <Icon className="h-4 w-4" />
        </span>
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{label}</p>
          <p className="mt-1 text-2xl font-bold text-slate-950">{value}</p>
          <p className="mt-1 text-sm text-slate-600">{detail}</p>
        </div>
      </div>
    </div>
  );
}

function Panel({ title, icon: Icon, children, aside }) {
  return (
    <section className="rounded-lg border border-slate-200 bg-white shadow-sm">
      <div className="flex items-center justify-between gap-4 border-b border-slate-200 px-5 py-4">
        <div className="flex items-center gap-3">
          <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-teal-50 text-teal-700">
            <Icon className="h-4 w-4" />
          </span>
          <h2 className="text-sm font-bold uppercase tracking-wide text-slate-800">{title}</h2>
        </div>
        {aside}
      </div>
      <div className="p-5">{children}</div>
    </section>
  );
}

function RiskBadge({ level }) {
  const normalized = level || "medium";
  return (
    <span className={`rounded-full border px-3 py-1 text-xs font-bold uppercase ${riskColors[normalized] || riskColors.medium}`}>
      {normalized}
    </span>
  );
}

export default function Dashboard() {
  const [mission, setMission] = useState(initialMission);
  const [result, setResult] = useState(fallbackResult);
  const [isRunning, setIsRunning] = useState(false);
  const [mode, setMode] = useState("demo");
  const [error, setError] = useState("");

  const utilization = useMemo(() => {
    const ratio = result?.agents?.forecast?.utilization_ratio ?? mission.expected_attendance / mission.venue_capacity;
    return Math.round(ratio * 100);
  }, [mission.expected_attendance, mission.venue_capacity, result]);

  const plan = result.operation_plan;
  const forecast = result.agents.forecast;
  const resources = result.agents.resources;
  const actions = result.agents.incidents.response_actions;

  function updateField(field, value) {
    setMission((prev) => ({ ...prev, [field]: value }));
  }

  async function runMission() {
    setIsRunning(true);
    setError("");
    const payload = {
      ...mission,
      expected_attendance: Number(mission.expected_attendance),
      venue_capacity: Number(mission.venue_capacity),
    };

    try {
      const next = await api.coordinate(payload);
      setResult(next);
      setMode("live");
    } catch (err) {
      setResult(fallbackResult);
      setMode("demo");
      setError(`Backend unavailable, showing demo execution: ${err.message}`);
    } finally {
      setIsRunning(false);
    }
  }

  return (
    <div className="min-h-screen bg-slate-100 text-slate-950">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-[1500px] flex-col gap-4 px-4 py-5 sm:px-6 lg:flex-row lg:items-center lg:justify-between lg:px-8">
          <div className="flex items-center gap-3">
            <span className="flex h-11 w-11 items-center justify-center rounded-lg bg-slate-950 text-teal-300">
              <IconRadar className="h-5 w-5" />
            </span>
            <div>
              <h1 className="text-2xl font-black tracking-tight text-slate-950">CrowdPilot AI</h1>
              <p className="text-sm text-slate-600">Supervised agent for real-world event operations</p>
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-2 text-xs font-semibold uppercase tracking-wide">
            <span className="rounded-full border border-teal-200 bg-teal-50 px-3 py-1 text-teal-800">Gemini agent workflow</span>
            <span className="rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 text-emerald-800">MongoDB MCP track</span>
            <span className="rounded-full border border-slate-300 bg-slate-50 px-3 py-1 text-slate-700">{mode === "live" ? "Live API" : "Demo fallback"}</span>
          </div>
        </div>
      </header>

      <main className="mx-auto grid max-w-[1500px] gap-5 px-4 py-5 sm:px-6 lg:grid-cols-[390px_1fr_390px] lg:px-8">
        <aside className="space-y-5">
          <Panel title="Mission Brief" icon={IconBuilding}>
            <div className="space-y-4">
              <Field label="Event">
                <input className={inputClass()} value={mission.event_name} onChange={(e) => updateField("event_name", e.target.value)} />
              </Field>
              <Field label="Venue">
                <input className={inputClass()} value={mission.venue} onChange={(e) => updateField("venue", e.target.value)} />
              </Field>
              <Field label="Operator goal">
                <textarea
                  className={`${inputClass()} min-h-28 resize-none`}
                  value={mission.mission_goal}
                  onChange={(e) => updateField("mission_goal", e.target.value)}
                />
              </Field>
              <div className="grid grid-cols-2 gap-3">
                <Field label="Attendance">
                  <input className={inputClass()} type="number" value={mission.expected_attendance} onChange={(e) => updateField("expected_attendance", e.target.value)} />
                </Field>
                <Field label="Capacity">
                  <input className={inputClass()} type="number" value={mission.venue_capacity} onChange={(e) => updateField("venue_capacity", e.target.value)} />
                </Field>
              </div>
              <Field label="Weather">
                <input className={inputClass()} value={mission.weather_condition} onChange={(e) => updateField("weather_condition", e.target.value)} />
              </Field>
              <Field label="Peak window">
                <input className={inputClass()} value={mission.time_window} onChange={(e) => updateField("time_window", e.target.value)} />
              </Field>
              <button
                type="button"
                onClick={runMission}
                disabled={isRunning}
                className="flex w-full items-center justify-center gap-2 rounded-lg bg-slate-950 px-4 py-3 text-sm font-bold text-white transition hover:bg-teal-800 disabled:cursor-wait disabled:opacity-70"
              >
                <IconPlay className="h-4 w-4" />
                {isRunning ? "Running agents..." : "Run multi-step mission"}
              </button>
              {error && <p className="rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-800">{error}</p>}
            </div>
          </Panel>

          <Panel title="Active Incidents" icon={IconAlert}>
            <div className="space-y-3">
              {mission.incident_data.map((incident) => (
                <div key={incident.id} className="rounded-lg border border-slate-200 bg-slate-50 p-3">
                  <div className="flex items-center justify-between gap-3">
                    <p className="text-sm font-bold text-slate-900">{incident.location}</p>
                    <RiskBadge level={incident.severity} />
                  </div>
                  <p className="mt-2 text-sm text-slate-600">{incident.description}</p>
                </div>
              ))}
            </div>
          </Panel>
        </aside>

        <section className="space-y-5">
          <div className="grid gap-4 md:grid-cols-3">
            <Metric icon={IconUsers} label="Utilization" value={`${utilization}%`} detail={`${Number(mission.expected_attendance).toLocaleString()} expected attendees`} />
            <Metric icon={IconActivity} label="Staffing" value={resources.recommended_security_staff} detail={`${resources.recommended_traffic_controllers} traffic, ${resources.recommended_medical_staff} medical`} />
            <Metric icon={IconAlert} label="Risk Level" value={plan.risk_level.toUpperCase()} detail={`${forecast.congestion_zones.length} congestion zones detected`} />
          </div>

          <Panel title="Generated Operation Plan" icon={IconRoute} aside={<RiskBadge level={plan.risk_level} />}>
            <p className="mb-4 text-sm leading-6 text-slate-600">{plan.mission_summary}</p>
            <div className="space-y-3">
              {plan.recommendations.map((item, index) => (
                <div key={item} className="flex gap-3 rounded-lg border border-slate-200 bg-slate-50 p-3">
                  <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-md bg-white font-mono text-xs font-bold text-teal-700 ring-1 ring-slate-200">
                    {index + 1}
                  </span>
                  <p className="text-sm leading-6 text-slate-800">{item}</p>
                </div>
              ))}
            </div>
          </Panel>

          <Panel title="Field Actions" icon={IconCheck}>
            <div className="grid gap-3 md:grid-cols-2">
              {actions.map((action) => (
                <div key={`${action.incident_ref}-${action.location}`} className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
                  <div className="mb-2 flex items-center justify-between gap-3">
                    <p className="text-sm font-bold text-slate-950">{action.location}</p>
                    <RiskBadge level={action.priority} />
                  </div>
                  <p className="text-sm leading-6 text-slate-600">{action.action}</p>
                </div>
              ))}
            </div>
          </Panel>
        </section>

        <aside className="space-y-5">
          <Panel title="Agent Execution" icon={IconRadar}>
            <div className="space-y-3">
              {plan.execution_steps.map((step, index) => (
                <div key={step} className="flex gap-3">
                  <span className="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-teal-600 text-xs font-bold text-white">
                    {index + 1}
                  </span>
                  <p className="text-sm leading-6 text-slate-700">{step}</p>
                </div>
              ))}
            </div>
          </Panel>

          <Panel title="Partner MCP Trail" icon={IconDatabase}>
            <div className="space-y-3">
              {plan.partner_tool_calls.map((call) => (
                <div key={`${call.tool}-${call.collection}`} className="rounded-lg border border-slate-200 bg-slate-50 p-3">
                  <div className="flex items-center justify-between gap-3">
                    <p className="font-mono text-sm font-bold text-slate-950">{call.tool}</p>
                    <span className="rounded-full bg-white px-2 py-1 text-[10px] font-bold uppercase text-slate-600 ring-1 ring-slate-200">
                      {call.status}
                    </span>
                  </div>
                  <p className="mt-1 text-xs font-semibold uppercase tracking-wide text-teal-700">{call.mcp_server}</p>
                  <p className="mt-2 text-sm leading-5 text-slate-600">{call.purpose}</p>
                  <p className="mt-2 font-mono text-xs text-slate-500">{call.collection}</p>
                </div>
              ))}
            </div>
          </Panel>

          <Panel title="Success Metrics" icon={IconActivity}>
            <ul className="space-y-3">
              {plan.success_metrics.map((metric) => (
                <li key={metric} className="flex gap-3 text-sm leading-6 text-slate-700">
                  <IconCheck className="mt-1 h-4 w-4 shrink-0 text-emerald-600" />
                  <span>{metric}</span>
                </li>
              ))}
            </ul>
          </Panel>
        </aside>
      </main>
    </div>
  );
}
