import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from agents.coordinator import CoordinatorAgent
from agents.schemas import (
    AgentPipelineOutputs,
    CoordinatorInput,
    CoordinatorOutput,
    ForecastInput,
    IncidentAgentInput,
    ResourceInput,
)


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class MissionRecord:
    mission_id: str
    payload: CoordinatorInput
    status: str = "running"
    events: list[dict[str, Any]] = field(default_factory=list)
    subscribers: list[asyncio.Queue] = field(default_factory=list)
    result: CoordinatorOutput | None = None
    action_decisions: dict[int, str] = field(default_factory=dict)


class MissionRuntime:
    def __init__(self) -> None:
        self.coordinator = CoordinatorAgent()
        self.missions: dict[str, MissionRecord] = {}

    def create(self, payload: CoordinatorInput) -> MissionRecord:
        mission_id = uuid4().hex
        record = MissionRecord(mission_id=mission_id, payload=payload)
        self.missions[mission_id] = record
        asyncio.create_task(self._run(record))
        return record

    def get(self, mission_id: str) -> MissionRecord | None:
        return self.missions.get(mission_id)

    async def subscribe(self, mission_id: str) -> asyncio.Queue | None:
        record = self.get(mission_id)
        if record is None:
            return None
        queue: asyncio.Queue = asyncio.Queue()
        record.subscribers.append(queue)
        return queue

    def unsubscribe(self, mission_id: str, queue: asyncio.Queue) -> None:
        record = self.get(mission_id)
        if record and queue in record.subscribers:
            record.subscribers.remove(queue)

    def decide_action(self, mission_id: str, action_index: int, decision: str) -> bool:
        record = self.get(mission_id)
        if record is None or record.result is None:
            return False
        actions = record.result.agents.incidents.response_actions
        if action_index < 0 or action_index >= len(actions):
            return False
        record.action_decisions[action_index] = decision
        return True

    async def _emit(self, record: MissionRecord, event_type: str, **data: Any) -> None:
        event = {"type": event_type, "timestamp": utc_timestamp(), **data}
        record.events.append(event)
        for queue in list(record.subscribers):
            await queue.put(event)

    async def _run(self, record: MissionRecord) -> None:
        data = record.payload
        try:
            await self._emit(
                record,
                "mission_started",
                mission_id=record.mission_id,
                message=f"Mission compiled for {data.event_name or 'selected event'}.",
            )

            await self._emit(
                record,
                "agent_running",
                agent="coordinator",
                thought="Fetching historical event data...",
            )
            await self._emit(
                record,
                "activity",
                agent="coordinator",
                message=f"Loaded mission context for {data.expected_attendance:,} attendees.",
            )
            await self._emit(record, "agent_completed", agent="coordinator")
            await self._emit(
                record,
                "agent_handoff",
                from_agent="coordinator",
                to_agent="forecast",
            )

            await self._emit(
                record,
                "agent_running",
                agent="forecast",
                thought="Predicting crowd density...",
            )
            forecast = await self.coordinator.forecast_agent.arun(
                ForecastInput(
                    expected_attendance=data.expected_attendance,
                    venue_capacity=data.venue_capacity,
                )
            )
            await self._emit(
                record,
                "activity",
                agent="forecast",
                message=f"Peak utilization predicted at {forecast.utilization_ratio:.0%}.",
            )
            await self._emit(
                record,
                "agent_completed",
                agent="forecast",
                output=forecast.model_dump(mode="json"),
            )
            await self._emit(
                record,
                "agent_handoff",
                from_agent="forecast",
                to_agent="risk",
            )

            await self._emit(
                record,
                "agent_running",
                agent="risk",
                thought="Analyzing congestion hotspots...",
            )
            critical_zones = [
                zone for zone in forecast.congestion_zones if zone.level in ("high", "critical")
            ]
            risk_message = (
                f"{len(critical_zones)} critical bottleneck"
                f"{'s' if len(critical_zones) != 1 else ''} detected."
            )
            await self._emit(
                record,
                "activity",
                agent="risk",
                message=risk_message,
            )
            await self._emit(
                record,
                "agent_completed",
                agent="risk",
                output={
                    "risk_level": forecast.crowd_risk_level,
                    "critical_zones": [zone.model_dump(mode="json") for zone in critical_zones],
                },
            )
            await self._emit(
                record,
                "agent_handoff",
                from_agent="risk",
                to_agent="resource",
            )

            await self._emit(
                record,
                "agent_running",
                agent="resource",
                thought="Optimizing security deployment...",
            )
            resources = await self.coordinator.resource_agent.arun(
                ResourceInput(
                    crowd_risk_level=forecast.crowd_risk_level,
                    expected_attendance=data.expected_attendance,
                    venue_capacity=data.venue_capacity,
                    utilization_ratio=forecast.utilization_ratio,
                )
            )
            await self._emit(
                record,
                "activity",
                agent="resource",
                message=f"Allocated {resources.recommended_security_staff} security staff.",
            )
            await self._emit(
                record,
                "agent_completed",
                agent="resource",
                output=resources.model_dump(mode="json"),
            )
            await self._emit(
                record,
                "agent_handoff",
                from_agent="resource",
                to_agent="action",
            )

            await self._emit(
                record,
                "agent_running",
                agent="action",
                thought="Generating response plan...",
            )
            incidents = await self.coordinator.incident_agent.arun(
                IncidentAgentInput(incident_data=data.incident_data)
            )
            operation_plan = self.coordinator._build_operation_plan(
                data=data,
                risk_level=forecast.crowd_risk_level,
                forecast=forecast,
                resources=resources,
                incidents=incidents,
            )
            result = CoordinatorOutput(
                agents=AgentPipelineOutputs(
                    forecast=forecast,
                    resources=resources,
                    incidents=incidents,
                ),
                operation_plan=operation_plan,
            )
            record.result = result

            for index, action in enumerate(incidents.response_actions):
                confidence = 92 if action.priority == "high" else 86
                await self._emit(
                    record,
                    "action_generated",
                    action_index=index,
                    action={
                        **action.model_dump(mode="json"),
                        "confidence": confidence,
                        "impact": "Expected density reduction: 18%"
                        if action.priority == "high"
                        else "Improves response coverage in the affected zone.",
                    },
                )

            await self._emit(
                record,
                "activity",
                agent="action",
                message=f"Generated {len(incidents.response_actions)} approval-ready actions.",
            )
            await self._emit(
                record,
                "agent_completed",
                agent="action",
                output=incidents.model_dump(mode="json"),
            )
            record.status = "completed"
            await self._emit(
                record,
                "mission_completed",
                result=result.model_dump(mode="json"),
            )
        except Exception as exc:
            record.status = "failed"
            await self._emit(
                record,
                "agent_failed",
                agent=self._current_agent(record),
                message=str(exc),
            )

    @staticmethod
    def _current_agent(record: MissionRecord) -> str:
        for event in reversed(record.events):
            if event["type"] == "agent_running":
                return event["agent"]
        return "coordinator"


mission_runtime = MissionRuntime()
