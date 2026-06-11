import { useEffect, useMemo, useRef, useState } from "react";
import AgentPipeline from "../components/AgentPipeline.jsx";
import { api, missionWebSocketUrl } from "../api/client.js";
import {
  IconActivity,
  IconAlert,
  IconCheck,
  IconPlay,
  IconRadar,
  IconRoute,
  IconUsers,
} from "../components/icons.jsx";

const eventOptions = [
  {
    id: "world-cup-final",
    name: "World Cup Final 2026",
    venue: "National Stadium",
    attendance: 80000,
    capacity: 88000,
    focus: "Crowd Safety",
    weather: "Clear, 28C",
    timeWindow: "17:00-23:30",
    mission:
      "Protect ingress and egress flow, detect critical crowd density early, and generate operator-approved mitigation actions.",
    incidents: [
      {
        id: "INC-1042",
        location: "Zone A - Gate B",
        severity: "high",
        description: "Arrival rate is exceeding gate throughput and queue density is rising.",
        status: "open",
      },
      {
        id: "INC-1041",
        location: "North Concourse",
        severity: "medium",
        description: "Pedestrian flow is converging near food and merchandise areas.",
        status: "in_progress",
      },
    ],
  },
  {
    id: "fan-zone",
    name: "City Fan Zone Final",
    venue: "Downtown Event Plaza",
    attendance: 42500,
    capacity: 50000,
    focus: "Surge Management",
    weather: "Humid, 31C",
    timeWindow: "18:00-22:30",
    mission:
      "Prevent entry bottlenecks, keep medical response under 8 minutes, and prepare the venue for the evening surge.",
    incidents: [
      {
        id: "INC-2042",
        location: "Main Ingress",
        severity: "high",
        description: "Queue depth exceeds 400m and wait time is trending above 35 minutes.",
        status: "open",
      },
      {
        id: "INC-2041",
        location: "Stage Front",
        severity: "medium",
        description: "Static density is increasing near the sponsor stage.",
        status: "in_progress",
      },
    ],
  },
  {
    id: "mall-launch",
    name: "Retail Launch Weekend",
    venue: "Harbor Mall Atrium",
    attendance: 18600,
    capacity: 24000,
    focus: "Shopper Flow",
    weather: "Indoor venue",
    timeWindow: "12:00-20:00",
    mission:
      "Balance shopper flow, prevent vertical transport choke points, and issue coordinated tenant and security actions.",
    incidents: [
      {
        id: "INC-3042",
        location: "West Escalators",
        severity: "high",
        description: "Two escalators are offline and crowd dwell time is increasing.",
        status: "open",
      },
    ],
  },
];

const agents = [
  {
    id: "coordinator",
    name: "Coordinator Agent",
    role: "Mission orchestration and context",
    thought: "Waiting for mission execution...",
  },
  {
    id: "forecast",
    name: "Crowd Forecast Agent",
    role: "Crowd flow and density prediction",
    thought: "Waiting for coordinator context...",
  },
  {
    id: "risk",
    name: "Risk Analysis Agent",
    role: "Congestion and bottleneck analysis",
    thought: "Waiting for forecast results...",
  },
  {
    id: "resource",
    name: "Resource Planner Agent",
    role: "Security and response allocation",
    thought: "Waiting for risk analysis...",
  },
  {
    id: "action",
    name: "Action Generation Agent",
    role: "Approval-ready response plans",
    thought: "Waiting for resource plan...",
  },
];

const initialAgentState = Object.fromEntries(
  agents.map((agent) => [
    agent.id,
    { status: "waiting", thought: agent.thought },
  ]),
);

const agentLabel = Object.fromEntries(agents.map((agent) => [agent.id, agent.name]));

function formatTime(timestamp) {
  return new Intl.DateTimeFormat("en", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
  }).format(timestamp ? new Date(timestamp) : new Date());
}

function StatusBadge({ status }) {
  const styles = {
    ready: "border-slate-200 bg-slate-100 text-slate-600",
    running: {dot: "bg-blue-500 animate-pulse",badge: "border-blue-200 bg-blue-50 text-blue-700",card: "border-blue-300 bg-blue-50 animate-pulse",},
    completed: "border-emerald-200 bg-emerald-50 text-emerald-700",
    failed: "border-red-200 bg-red-50 text-red-700",
  };

  return (
    <span className={`inline-flex items-center gap-2 rounded-full border px-3 py-1 text-[10px] font-black uppercase ${styles[status] || styles.ready}`}>
      <span className={`h-2 w-2 rounded-full ${status === "running" ? "bg-blue-500" : status === "completed" ? "bg-emerald-500" : status === "failed" ? "bg-red-500" : "bg-slate-400"}`} />
      {status}
    </span>
  );
}

function OperationalView({ forecast, status }) {
  const zones = forecast?.congestion_zones || [];
  const critical = zones.find((zone) => zone.level === "critical") || zones[0];
  const density = forecast ? Math.round(forecast.utilization_ratio * 100) : 0;

  return (
    <section className="h-full min-h-0 rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
      <div className="mb-3 flex items-center justify-between">
        <div>
          <p className="text-[10px] font-bold uppercase tracking-[0.14em] text-blue-700">Operational visualization</p>
          <h2 className="text-base font-black text-slate-950">Venue Density Forecast</h2>
        </div>
        <span className="text-[10px] font-bold uppercase text-slate-500">{status === "running" ? "Live prediction" : "Current view"}</span>
      </div>

      <div className="grid h-[calc(100%-46px)] min-h-[260px] grid-cols-[minmax(0,1fr)_112px] gap-3">
        <div className="relative h-full overflow-hidden rounded-md border border-slate-200 bg-slate-50">
          <div className="absolute inset-[14%_9%] rounded-[42%] border-[18px] border-emerald-200 bg-emerald-100" />
          <div className="absolute inset-[20%_14%] rounded-[42%] border-[18px] border-yellow-200 bg-yellow-100" />
          <div className="absolute inset-[27%_20%] rounded-[40%] border-[15px] border-orange-300 bg-orange-100" />
          <div className={`absolute inset-[34%_28%] rounded-[34%] border-[12px] ${density >= 85 ? "border-red-400 bg-red-100" : density ? "border-orange-300 bg-orange-50" : "border-slate-200 bg-white"}`} />
          <div className="absolute inset-[40%_34%] rounded-md border border-emerald-300 bg-emerald-500/70" />
          {["A1", "B1", "C1"].map((zone, index) => (
            <span
              key={zone}
              className="absolute rounded-md border border-slate-200 bg-white px-2 py-1 text-[10px] font-black shadow-sm"
              style={{
                left: `${43 + index * 8}%`,
                top: `${20 + index * 25}%`,
              }}
            >
              {zone}
            </span>
          ))}
          <span className="absolute left-1/2 top-2 -translate-x-1/2 rounded-md border border-slate-200 bg-white px-2 py-1 text-[9px] font-black">GATE A</span>
          <span className="absolute bottom-2 left-1/2 -translate-x-1/2 rounded-md border border-slate-200 bg-white px-2 py-1 text-[9px] font-black">GATE C</span>
          <span className="absolute left-2 top-1/2 -translate-y-1/2 rounded-md border border-slate-200 bg-white px-2 py-1 text-[9px] font-black">GATE D</span>
          <span className="absolute right-2 top-1/2 -translate-y-1/2 rounded-md border border-slate-200 bg-white px-2 py-1 text-[9px] font-black">GATE B</span>
        </div>

        <div className="space-y-2">
          <div className="rounded-md border border-slate-200 bg-slate-50 p-3">
            <p className="text-[9px] font-bold uppercase text-slate-500">Predicted density</p>
            <p className={`mt-1 text-2xl font-black ${density >= 85 ? "text-red-600" : "text-slate-950"}`}>{density ? `${density}%` : "--"}</p>
          </div>
          <div className="rounded-md border border-slate-200 bg-slate-50 p-3">
            <p className="text-[9px] font-bold uppercase text-slate-500">Critical zone</p>
            <p className="mt-1 truncate text-sm font-black text-slate-950">{critical?.zone || "--"}</p>
          </div>
          <div className="rounded-md border border-slate-200 bg-slate-50 p-3">
            <p className="text-[9px] font-bold uppercase text-slate-500">Trend</p>
            <p className="mt-1 text-sm font-black text-slate-950">{density ? "Increasing" : "Awaiting run"}</p>
          </div>
        </div>
      </div>
    </section>
  );
}

function ActivityFeed({ items }) {
  return (
    <section className="min-h-0 rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
      <div className="mb-3">
        <p className="text-[10px] font-bold uppercase tracking-[0.14em] text-blue-700">Reason · Plan · Execute</p>
        <h2 className="text-base font-black text-slate-950">Agent Activity Feed</h2>
      </div>
      <div className="max-h-[190px] space-y-1 overflow-auto pr-1 xl:max-h-[calc(100%-44px)]">
        {items.length === 0 ? (
          <div className="rounded-md border border-dashed border-slate-300 px-4 py-8 text-center text-xs text-slate-500">
            Activity appears here after Execute Mission.
          </div>
        ) : (
          items.map((item, index) => (
            <div key={`${item.timestamp}-${index}`} className="grid grid-cols-[70px_120px_minmax(0,1fr)] gap-2 border-b border-slate-100 px-2 py-2.5 text-xs">
              <span className="font-mono text-blue-700">{formatTime(item.timestamp)}</span>
              <span className="truncate font-black text-slate-950">{agentLabel[item.agent] || "Mission Control"}</span>
              <span className="text-slate-600">{item.message}</span>
            </div>
          ))
        )}
      </div>
    </section>
  );
}

function MissionSummary({ status, agentState, actions, result }) {
  const completed = Object.values(agentState).filter((agent) => agent.status === "completed").length;
  const confidence = actions.length
    ? Math.round(actions.reduce((sum, action) => sum + action.confidence, 0) / actions.length)
    : null;

  return (
    <section className="rounded-lg border border-slate-200 bg-white p-3 shadow-sm">
      <div className="grid grid-cols-4 gap-2">
        {[
          ["Mission status", status],
          ["Agents completed", `${completed} / ${agents.length}`],
          ["Actions generated", actions.length],
          ["Confidence score", confidence ? `${confidence}%` : "--"],
        ].map(([label, value]) => (
          <div key={label} className="rounded-md border border-slate-200 bg-slate-50 px-3 py-2">
            <p className="text-[9px] font-bold uppercase tracking-[0.08em] text-slate-500">{label}</p>
            <p className="mt-1 truncate text-sm font-black capitalize text-slate-950">{value}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

function ActionPlans({ missionId, actions, decisions, onDecision }) {
  async function decide(index, decision) {
    await api.decideAction(missionId, index, decision);
    onDecision(index, decision);
  }

  return (
    <section className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
      <div className="mb-3 flex items-center justify-between">
        <div>
          <p className="text-[10px] font-bold uppercase tracking-[0.14em] text-blue-700">Human oversight</p>
          <h2 className="text-base font-black text-slate-950">Generated Action Plans</h2>
        </div>
        <span className="text-[10px] font-bold uppercase text-slate-500">Approval required</span>
      </div>
      <div className="grid max-h-[190px] gap-2 overflow-auto pr-1 xl:max-h-[calc(100%-44px)]">
        {actions.length === 0 ? (
          <div className="col-span-2 rounded-md border border-dashed border-slate-300 px-4 py-7 text-center text-xs text-slate-500">
            Approval-ready actions are generated by the final agent.
          </div>
        ) : (
          actions.map((action, index) => {
            const decision = decisions[index];
            return (
              <div key={`${action.incident_ref}-${index}`} className="rounded-md border border-slate-200 bg-slate-50 p-3">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="text-[10px] font-bold uppercase text-blue-700">Action #{index + 1}</p>
                    <h3 className="mt-1 text-sm font-black text-slate-950">{action.action}</h3>
                  </div>
                  <span className="rounded-full border border-emerald-200 bg-emerald-50 px-2 py-1 text-[9px] font-black text-emerald-700">
                    {action.confidence}%
                  </span>
                </div>
                <p className="mt-2 text-[11px] text-slate-600"><strong>Reason:</strong> {action.location} requires intervention.</p>
                <p className="mt-1 text-[11px] text-slate-600"><strong>Impact:</strong> {action.impact}</p>
                <div className="mt-3 flex gap-2">
                  <button
                    type="button"
                    disabled={Boolean(decision)}
                    onClick={() => decide(index, "approved")}
                    className="flex-1 rounded-md bg-slate-950 px-3 py-2 text-[10px] font-black uppercase text-white disabled:opacity-45"
                  >
                    {decision === "approved" ? "Approved" : "Approve"}
                  </button>
                  <button
                    type="button"
                    disabled={Boolean(decision)}
                    onClick={() => decide(index, "rejected")}
                    className="flex-1 rounded-md border border-slate-300 bg-white px-3 py-2 text-[10px] font-black uppercase text-slate-700 disabled:opacity-45"
                  >
                    {decision === "rejected" ? "Rejected" : "Reject"}
                  </button>
                </div>
              </div>
            );
          })
        )}
      </div>
    </section>
  );
}

export default function Dashboard() {
  const [eventId, setEventId] = useState(eventOptions[0].id);
  const [missionId, setMissionId] = useState("");
  const [missionStatus, setMissionStatus] = useState("ready");
  const [agentState, setAgentState] = useState(initialAgentState);
  const [handoff, setHandoff] = useState(null);
  const [activity, setActivity] = useState([]);
  const [actions, setActions] = useState([]);
  const [decisions, setDecisions] = useState({});
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const socketRef = useRef(null);

  const event = eventOptions.find((item) => item.id === eventId) || eventOptions[0];
  const forecast = result?.agents?.forecast;

  const payload = useMemo(
    () => ({
      event_name: event.name,
      venue: event.venue,
      mission_goal: event.mission,
      expected_attendance: event.attendance,
      venue_capacity: event.capacity,
      weather_condition: event.weather,
      time_window: event.timeWindow,
      incident_data: event.incidents,
    }),
    [event],
  );

  useEffect(() => () => socketRef.current?.close(), []);

  function applyEvent(message) {
    if (message.type === "mission_started") {
      setMissionStatus("running");
      setActivity((prev) => [...prev, { ...message, agent: "coordinator" }]);
    }

    if (message.type === "agent_running") {
      setAgentState((prev) => ({
        ...prev,
        [message.agent]: { status: "running", thought: message.thought },
      }));
    }

    if (message.type === "agent_completed") {
      setAgentState((prev) => ({
        ...prev,
        [message.agent]: { ...prev[message.agent], status: "completed" },
      }));
    }

    if (message.type === "agent_failed") {
      setMissionStatus("failed");
      setAgentState((prev) => ({
        ...prev,
        [message.agent]: { ...prev[message.agent], status: "failed", thought: message.message },
      }));
      setError(message.message);
    }

    if (message.type === "agent_handoff") {
      setHandoff(message);
    }

    if (message.type === "activity") {
      setActivity((prev) => [...prev, message]);
    }

    if (message.type === "action_generated") {
      setActions((prev) => {
        if (prev.some((item) => item.action_index === message.action_index)) return prev;
        return [...prev, { ...message.action, action_index: message.action_index }];
      });
    }

    if (message.type === "mission_completed") {
      setMissionStatus("completed");
      setResult(message.result);
      setHandoff(null);
    }
  }

  function connectMissionSocket(nextMissionId) {
    socketRef.current?.close();
    const socket = new WebSocket(missionWebSocketUrl(nextMissionId));
    socketRef.current = socket;
    socket.onmessage = (eventMessage) => applyEvent(JSON.parse(eventMessage.data));
    socket.onerror = () => setError("Mission event stream disconnected.");
  }

  async function executeMission() {
    setMissionStatus("running");
    setAgentState(initialAgentState);
    setHandoff(null);
    setActivity([]);
    setActions([]);
    setDecisions({});
    setResult(null);
    setError("");

    try {
      const started = await api.startMission(payload);
      setMissionId(started.mission_id);
      connectMissionSocket(started.mission_id);
    } catch (err) {
      setMissionStatus("failed");
      setError(err.message);
    }
  }

  return (
    <div className="min-h-screen bg-[#f7f9fc] text-slate-950">
      <header className="h-16 border-b border-slate-200 bg-white">
        <div className="mx-auto flex h-full max-w-[1540px] items-center justify-between px-5">
          <div className="flex items-center gap-3">
            <span className="grid h-10 w-10 place-items-center rounded-md bg-blue-600 text-white">
              <IconRadar className="h-5 w-5" />
            </span>
            <div>
              <h1 className="text-xl font-black tracking-tight">CrowdPilot</h1>
              <p className="text-[10px] font-bold uppercase tracking-[0.12em] text-slate-500">AI Agent Mission Control</p>
            </div>
          </div>
          <div className="flex items-center gap-5">
            <span className="hidden text-xs font-bold text-slate-500 sm:block">Mission Control</span>
            <StatusBadge status={missionStatus === "ready" ? "ready" : missionStatus} />
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-[1540px] space-y-3 px-5 py-3">
        <section className="grid items-center gap-4 rounded-lg border border-slate-200 bg-white px-5 py-4 shadow-sm lg:grid-cols-[minmax(0,1fr)_250px_180px]">
          <div>
            <p className="text-[10px] font-bold uppercase tracking-[0.14em] text-blue-700">Current mission</p>
            <div className="mt-1 flex flex-wrap items-end gap-x-6 gap-y-2">
              <div>
                <select
                  aria-label="Select Event"
                  value={eventId}
                  onChange={(changeEvent) => setEventId(changeEvent.target.value)}
                  disabled={missionStatus === "running"}
                  className="max-w-full bg-transparent text-2xl font-black tracking-tight outline-none disabled:opacity-60"
                >
                  {eventOptions.map((option) => (
                    <option key={option.id} value={option.id}>{option.name}</option>
                  ))}
                </select>
              </div>
              {[
                ["Venue", event.venue],
                ["Expected attendance", event.attendance.toLocaleString()],
                ["Operational focus", event.focus],
                ["Conditions", event.weather],
              ].map(([label, value]) => (
                <div key={label}>
                  <p className="text-[9px] font-bold uppercase tracking-[0.08em] text-slate-500">{label}</p>
                  <p className="mt-0.5 text-xs font-black text-slate-950">{value}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-md border border-slate-200 bg-slate-50 p-3">
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-black uppercase text-slate-500">Mission status</span>
              <StatusBadge status={missionStatus} />
            </div>
            <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-slate-200">
              <div
                className={`h-full rounded-full transition-all ${missionStatus === "completed" ? "w-full bg-emerald-500" : missionStatus === "running" ? "w-2/3 bg-blue-500" : missionStatus === "failed" ? "w-full bg-red-500" : "w-0"}`}
              />
            </div>
          </div>

          <button
            type="button"
            onClick={executeMission}
            disabled={missionStatus === "running"}
            className="flex items-center justify-center gap-2 rounded-md bg-blue-600 px-4 py-3 text-sm font-black text-white shadow-sm transition hover:bg-blue-700 disabled:cursor-wait disabled:opacity-55"
          >
            <IconPlay className="h-4 w-4" />
            {missionStatus === "running" ? "Mission Running" : "Execute Mission"}
          </button>
        </section>

        {error && (
          <div className="rounded-md border border-red-200 bg-red-50 px-4 py-2 text-xs font-semibold text-red-700">
            {error}
          </div>
        )}

        <div className="grid gap-3 xl:h-[calc(100vh-224px)] xl:min-h-0 xl:grid-cols-[390px_minmax(0,1fr)_390px]">
          <div className="grid min-h-0 gap-3 xl:grid-rows-[minmax(0,1fr)_auto]">
            <AgentPipeline agents={agents} agentState={agentState} handoff={handoff} />
            <MissionSummary status={missionStatus} agentState={agentState} actions={actions} result={result} />
          </div>

          <OperationalView forecast={forecast} status={missionStatus} />

          <div className="grid min-h-0 gap-3 xl:grid-rows-[minmax(0,0.92fr)_minmax(0,1.08fr)]">
            <ActivityFeed items={activity} />
            <ActionPlans
              missionId={missionId}
              actions={actions}
              decisions={decisions}
              onDecision={(index, decision) => setDecisions((prev) => ({ ...prev, [index]: decision }))}
            />
          </div>
        </div>
      </main>
    </div>
  );
}
