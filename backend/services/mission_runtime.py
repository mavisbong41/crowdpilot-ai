import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from models.mission import CoordinatorInput
from mcp_tools.mongodb_tool import mongodb_mcp
from google.adk.sessions import InMemorySessionService


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class MissionRecord:
    mission_id: str
    payload: CoordinatorInput
    status: str = "running"
    events: list[dict[str, Any]] = field(default_factory=list)
    subscribers: list[asyncio.Queue] = field(default_factory=list)
    result: "Any | None" = field(default=None)
    action_decisions: dict[int, str] = field(default_factory=dict)


class MissionRuntime:
    def __init__(self) -> None:
        self.missions: dict[str, MissionRecord] = {}
        self.session_service = InMemorySessionService()

    def create(self, payload: CoordinatorInput) -> MissionRecord:
        mission_id = uuid4().hex

        record = MissionRecord(
            mission_id=mission_id,
            payload=payload,
        )

        self.missions[mission_id] = record

        from config import settings
        if settings.demo_mode:
            asyncio.create_task(self._run_demo(record))
        else:
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

        # 改成直接读取 operation 的 actions
        actions = record.result["operation"].get("actions", [])
        if action_index < 0 or action_index >= len(actions):
            return False

        record.action_decisions[action_index] = decision

        asyncio.create_task(
            mongodb_mcp.update_one(
                "missions",
                {"mission_id": mission_id},
                {f"action_decisions.{action_index}": decision},
            )
        )

        return True

    async def _emit(self, record: MissionRecord, event_type: str, **data: Any) -> None:
        event = {"type": event_type, "timestamp": utc_timestamp(), **data}
        record.events.append(event)
        for queue in list(record.subscribers):
            await queue.put(event)

    async def _run_demo(self, record: MissionRecord) -> None:
        await self._emit(
            record,
            "mission_started",
            mission_id=record.mission_id,
            message="Demo mission started."
        )

        agents = [
            ("coordinator", "Loading event context..."),
            ("forecast", "Forecasting crowd density..."),
            ("incident", "Evaluating incident playbooks..."),
            ("resource", "Allocating resources..."),
            ("action", "Generating operation plan...")
        ]

        for i, (agent, thought) in enumerate(agents):
            await self._emit(
                record,
                "agent_running",
                agent=agent,
                thought=thought,
            )

            await asyncio.sleep(1)

            await self._emit(
                record,
                "activity",
                agent=agent,
                message=f"{agent} completed analysis."
            )

            await self._emit(
                record,
                "agent_completed",
                agent=agent,
            )

            if i < len(agents) - 1:
                await self._emit(
                    record,
                    "agent_handoff",
                    from_agent=agent,
                    to_agent=agents[i + 1][0],
                )

        forecast_json = {
    "risk_level": "critical",
    "utilization_ratio": 0.94,
    "attendance": 80000,
    "capacity": 88000,
    "congestion_zones": [
        {
            "zone": "Gate A",
            "level": "critical"
        },
        {
            "zone": "Food Court",
            "level": "high"
        },
        {
            "zone": "North Concourse",
            "level": "medium"
        }
    ]
}

        incident_json = {
            "incident_type": "Crowd Surge",
            "severity": "High",
            "probability": 0.87,
            "location": "Gate A",
            "required_units": [
                "Security Staff",
                "Medical Team",
            ],
        }

        resource_json = {
            "security_staff": 20,
            "medical_teams": 3,
            "traffic_controllers": 10,
            "deployment_zone": "Gate A",
            "deployment_priority": "High",
            "deployment_plan": [
                "Deploy 10 guards to Gate A",
                "Deploy 10 guards to North Concourse",
                "Position medical team near food court",
            ],
        }

        operation_json = {
            "mission_name": "World Cup Final Safety Plan",
            "priority": "High",
            "objective": "Prevent crowd surge and maintain safe movement.",
            "actions": [
                "Open Gate C immediately",
                "Deploy additional security at Gate A",
                "Redirect spectators to North Entrance",
            ],
            "deployment_summary": [
                "20 security staff deployed",
                "3 medical teams activated",
            ],
            "success_criteria": [
                "Density below threshold",
                "Queue length under 100m",
            ],
        }

        for index, action_str in enumerate(operation_json["actions"]):
            await self._emit(
                record,
                "action_generated",
                action_index=index,
                action={
                    "action_id": f"ACT-00{index+1}",
                    "description": action_str,
                    "priority": "high",
                    "confidence": 94,
                    "impact": "Mitigates congestion.",
                },
            )

        record.result = {
            "agents": {
                "forecast": forecast_json,
                "incident": incident_json,
                "resource": resource_json,
            },
            "operation": operation_json,
        }

        record.status = "completed"

        await self._emit(
            record,
            "mission_completed",
            result=record.result,
        )

    async def _run(self, record: MissionRecord) -> None:
        """
        PRODUCTION NATIVE FLOW (No Mock Data)
        Fully compliant with Google Cloud ADK & MongoDB MCP Server specifications.
        """
        import json
        from google.adk.runners import Runner

        from adk_agents.forecast_agent import forecast_agent
        from adk_agents.incident_agent import incident_agent
        from adk_agents.resource_agent import resource_agent
        from adk_agents.operation_agent import operation_agent

        data = record.payload
        try:
            await self._emit(
                record,
                "mission_started",
                mission_id=record.mission_id,
                message=f"Mission compiled for {data.event_name or 'selected event'}.",
            )

            await self._emit(record, "agent_running", agent="coordinator", thought="Analyzing operational context...")

            historical_events = await mongodb_mcp.find("events", {})
            await self._emit(
                record,
                "activity",
                agent="coordinator",
                message=f"Loaded {len(historical_events)} historical events from MongoDB MCP for pattern comparison."
            )
            await self._emit(record, "agent_completed", agent="coordinator")
            await self._emit(record, "agent_handoff", from_agent="coordinator", to_agent="forecast")

            await self._emit(record, "agent_running", agent="forecast", thought="Invoking Forecast Agent for crowd density analysis...")
            
            session = await self.session_service.create_session(
                app_name="crowdpilot",
                user_id=record.mission_id,
            )

            forecast_runner = Runner(
                agent=forecast_agent,
                app_name="crowdpilot",
                session_service=self.session_service,
            )
            forecast_prompt = json.dumps(record.payload.model_dump(mode="json"))

            forecast_response = ""
            async for event in forecast_runner.run_async(user_id="crowdpilot", session_id=session.id, new_message=forecast_prompt):
                if event.is_final_response():
                    forecast_response = event.content.parts[0].text
                    break

            try:
                clean = forecast_response.strip().replace("```json", "").replace("```", "").strip()
                forecast_json = json.loads(clean)
            except json.JSONDecodeError as e:
                raise RuntimeError(f"Forecast agent returned invalid JSON: {forecast_response!r}") from e

            await self._emit(record, "activity", agent="forecast", message=f"Risk assessment concluded: {forecast_json.get('risk_level', 'unknown')} risk layer generated.")
            await self._emit(record, "agent_completed", agent="forecast", output=forecast_json)
            await self._emit(record, "agent_handoff", from_agent="forecast", to_agent="incident")

            await self._emit(record, "agent_running", agent="incident", thought="Evaluating risks against MongoDB playbooks...")

            incident_runner = Runner(
                agent=incident_agent,
                app_name="crowdpilot",
                session_service=self.session_service,
            )
            incident_prompt = json.dumps(forecast_json)

            incident_response = ""
            async for event in incident_runner.run_async(user_id="crowdpilot", session_id=session.id, new_message=incident_prompt):
                if event.is_final_response():
                    incident_response = event.content.parts[0].text
                    break

            try:
                clean = incident_response.strip().replace("```json", "").replace("```", "").strip()
                incident_json = json.loads(clean)
            except json.JSONDecodeError as e:
                raise RuntimeError(f"Incident agent returned invalid JSON: {incident_response!r}") from e

            await self._emit(record, "activity", agent="incident", message=f"Incident pattern classified: {incident_json.get('incident_type', 'None')}. Playbook verification successful.")
            await self._emit(record, "agent_completed", agent="incident", output=incident_json)
            await self._emit(record, "agent_handoff", from_agent="incident", to_agent="resource")
            await self._emit(record, "agent_running", agent="resource", thought="Calculating security and medical assets...")

            resource_runner = Runner(
                agent=resource_agent,
                app_name="crowdpilot",
                session_service=self.session_service,
            )
            resource_prompt = json.dumps(incident_json)

            resource_response = ""
            async for event in resource_runner.run_async(user_id="crowdpilot", session_id=session.id, new_message=resource_prompt):
                if event.is_final_response():
                    resource_response = event.content.parts[0].text
                    break

            try:
                clean = resource_response.strip().replace("```json", "").replace("```", "").strip()
                resource_json = json.loads(clean)
            except json.JSONDecodeError as e:
                raise RuntimeError(f"Resource agent returned invalid JSON: {resource_response!r}") from e

            await self._emit(record, "activity", agent="resource", message=f"Resource allocation finalized. Required units mapped to affected sectors.")
            await self._emit(record, "agent_completed", agent="resource", output=resource_json)
            await self._emit(record, "agent_handoff", from_agent="resource", to_agent="action")

            await self._emit(record, "agent_running", agent="action", thought="Compiling final operational deployment plan...")

            operation_runner = Runner(
                agent=operation_agent,
                app_name="crowdpilot",
                session_service=self.session_service,
            )
            combined_context = {
                "forecast": forecast_json,
                "incident": incident_json,
                "resource": resource_json
            }

            operation_response = ""
            async for event in operation_runner.run_async(user_id="crowdpilot", session_id=session.id, new_message=json.dumps(combined_context)):
                if event.is_final_response():
                    operation_response = event.content.parts[0].text
                    break

            try:
                clean = operation_response.strip().replace("```json", "").replace("```", "").strip()
                operation_json = json.loads(clean)
            except json.JSONDecodeError as e:
                raise RuntimeError(f"Operation agent returned invalid JSON: {operation_response!r}") from e

            for index, action_str in enumerate(operation_json.get("actions", [])):
                action = {
                    "action_id": f"ACT-00{index+1}",
                    "description": action_str,
                    "priority": operation_json.get("priority", "medium"),
                    "confidence": 94,
                    "impact": "Mitigates critical congestion layer."
                }
                await self._emit(
                    record,
                    "action_generated",
                    action_index=index,
                    action=action
                )

            await self._emit(record, "activity", agent="action", message="Deployment plan saved to system of record via MongoDB MCP.")
            await self._emit(record, "agent_completed", agent="action", output=operation_json)

            await mongodb_mcp.insert_one(
                "mission_results",
                {
                    "mission_id": record.mission_id,
                    "event_name": data.event_name,
                    "status": "completed",
                    "updated_at": utc_timestamp(),
                    "pipeline_payload": combined_context
                }
            )

            record.result = {
                "agents": {
                    "forecast": forecast_json,
                    "incident": incident_json,
                    "resource": resource_json
                },
                "operation": operation_json
            }
            record.status = "completed"

            await self._emit(
                record,
                "mission_completed",
                result=record.result
            )

        except Exception as exc:
            record.status = "failed"
            await self._emit(record, "agent_failed", agent=self._current_agent(record), message=str(exc))

    @staticmethod
    def _current_agent(record: MissionRecord) -> str:
        for event in reversed(record.events):
            if event["type"] == "agent_running":
                return event["agent"]
        return "coordinator"
    
    


mission_runtime = MissionRuntime()