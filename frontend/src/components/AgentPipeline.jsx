import { useEffect, useRef } from "react";
import { IconActivity, IconCheck, IconRadar, IconRoute } from "./icons.jsx";

const statusStyle = {
  waiting: {
    dot: "bg-slate-300",
    badge: "border-slate-200 bg-slate-100 text-slate-500",
    card: "border-slate-200 bg-white",
  },
  running: {
    dot: "bg-blue-500",
    badge: "border-blue-200 bg-blue-50 text-blue-700",
    card: "border-blue-300 bg-blue-50/40 shadow-[0_12px_40px_rgba(59,130,246,0.12)]",
  },
  completed: {
    dot: "bg-emerald-500",
    badge: "border-emerald-200 bg-emerald-50 text-emerald-700",
    card: "border-emerald-200 bg-emerald-50/30",
  },
  failed: {
    dot: "bg-red-500",
    badge: "border-red-200 bg-red-50 text-red-700",
    card: "border-red-200 bg-red-50/40",
  },
};

const agentIcons = [IconRadar, IconActivity, IconRoute, IconCheck, IconActivity];

export default function AgentPipeline({ agents, agentState, handoff }) {

  const cardRef = useRef({});

  useEffect(() => {
    const runningAgent = agents.find(
      (agent) => agentState[agent.id]?.status === "running"
    );

    if (
      runningAgent &&
      cardRef.current[runningAgent.id]
    ) {
      cardRef.current[runningAgent.id].scrollIntoView({
        behavior: "smooth",
        block: "center",
      });
    }
  }, [agentState, agents]);

  return (
    <section className="h-full min-h-0 flex flex-col rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
      <div className="mb-2 flex items-center justify-between">
        <div>
          <p className="text-[10px] font-bold uppercase tracking-[0.14em] text-blue-700">Agent topology</p>
          <h2 className="text-base font-black text-slate-950">Orchestration Pipeline</h2>
        </div>
        <span className="flex items-center gap-2 rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-[10px] font-bold uppercase text-slate-600">
          <span className="h-2 w-2 rounded-full bg-emerald-500" />
          Backend events
        </span>
      </div>

      <div className="flex-1 overflow-y-auto pr-2 space-y-0">
        {agents.map((agent, index) => {
          const state = agentState[agent.id] || { status: "waiting", thought: agent.thought };
          const style = statusStyle[state.status] || statusStyle.waiting;
          const AgentIcon = agentIcons[index];
          const handoffActive =
            handoff?.from_agent === agent.id && handoff?.to_agent === agents[index + 1]?.id;

          return (
            <div key={agent.id}>
              <div
              ref={(el) => (cardRef.current[agent.id] = el)}
              className={`grid grid-cols-[40px_minmax(0,1.3fr)_150px] gap-3 rounded-lg border px-3 py-3 transition ${style.card}`}>
                <span className="grid h-8 w-8 place-items-center rounded-md border border-slate-200 bg-white text-slate-700">
                  <AgentIcon className="h-4 w-4" />
                </span>
                <div className="min-w-0">
                  <div className="flex flex-col items-start gap-1">
                    <p className="text-sm font-black leading-tight text-slate-950"> {agent.name}</p>
                    <span className={`shrink-0 rounded-full border px-2 py-0.5 text-[9px] font-black uppercase ${style.badge}`}>
                      {state.status}
                    </span>
                  </div>
                  <p className="mt-1 text-[11px] leading-relaxed text-slate-500">{agent.role}</p>
                </div>
                <div className="min-w-0 rounded-md border border-slate-200 bg-white/90 px-2.5 py-2">
                  <p className="text-[11px] leading-relaxed text-slate-700">
                    {state.thought || agent.thought}
                  </p>
                </div>
              </div>

              {index < agents.length - 1 && (
                <div className="relative ml-[28px] h-3 w-px bg-slate-200">
                  <span
                    className={`absolute left-1/2 top-0 h-full w-px -translate-x-1/2 transition ${
                      handoffActive ? "bg-blue-500 shadow-[0_0_10px_rgba(59,130,246,0.9)]" : ""
                    }`}
                  />
                  <span className={`absolute -bottom-0.5 left-1/2 h-1.5 w-1.5 -translate-x-1/2 rotate-45 border-b border-r ${handoffActive ? "border-blue-500" : "border-slate-300"}`} />
                </div>
              )}
            </div>
          );
        })}
      </div>

      <div className="mt-2 flex items-center gap-4 border-t border-slate-100 pt-2 text-[10px] font-semibold text-slate-500">
        {Object.entries(statusStyle).map(([status, style]) => (
          <span key={status} className="flex items-center gap-1.5">
            <span className={`h-2 w-2 rounded-full ${style.dot}`} />
            {status[0].toUpperCase() + status.slice(1)}
          </span>
        ))}
      </div>
    </section>
  );
}
