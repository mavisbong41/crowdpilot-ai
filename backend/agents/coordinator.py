import asyncio
import logging

from agents.forecast import ForecastAgent
from agents.incident import IncidentAgent
from agents.resource import ResourceAgent
from agents.schemas import (
    AgentPipelineOutputs,
    CoordinatedOperationPlan,
    CoordinatorInput,
    CoordinatorOutput,
    ForecastInput,
    IncidentAgentInput,
    PartnerToolCall,
    ResourceInput,
)
from models.operation_plan import RiskLevel

logger = logging.getLogger("crowdpilot.agents.coordinator")


class CoordinatorAgent:
    """
    Orchestrates Forecast → Resource → Incident agents and synthesizes
    a final operation plan. Each sub-agent remains independently callable.
    """

    name = "coordinator"

    def __init__(
        self,
        forecast_agent: ForecastAgent | None = None,
        resource_agent: ResourceAgent | None = None,
        incident_agent: IncidentAgent | None = None,
    ) -> None:
        self.forecast_agent = forecast_agent or ForecastAgent()
        self.resource_agent = resource_agent or ResourceAgent()
        self.incident_agent = incident_agent or IncidentAgent()

    def run(self, data: CoordinatorInput) -> CoordinatorOutput:
        logger.info(
            "Coordinator pipeline start event=%s attendance=%s capacity=%s incidents=%s",
            data.event_name or "unnamed",
            data.expected_attendance,
            data.venue_capacity,
            len(data.incident_data),
        )
        forecast_output = self.forecast_agent.run(
            ForecastInput(
                expected_attendance=data.expected_attendance,
                venue_capacity=data.venue_capacity,
            )
        )

        resource_output = self.resource_agent.run(
            ResourceInput(
                crowd_risk_level=forecast_output.crowd_risk_level,
                expected_attendance=data.expected_attendance,
                venue_capacity=data.venue_capacity,
                utilization_ratio=forecast_output.utilization_ratio,
            )
        )

        incident_output = self.incident_agent.run(
            IncidentAgentInput(incident_data=data.incident_data)
        )

        operation_plan = self._build_operation_plan(
            data=data,
            risk_level=forecast_output.crowd_risk_level,
            forecast=forecast_output,
            resources=resource_output,
            incidents=incident_output,
        )

        output = CoordinatorOutput(
            agents=AgentPipelineOutputs(
                forecast=forecast_output,
                resources=resource_output,
                incidents=incident_output,
            ),
            operation_plan=operation_plan,
        )
        logger.info(
            "Coordinator pipeline complete risk=%s recommendations=%s",
            output.operation_plan.risk_level,
            len(output.operation_plan.recommendations),
        )
        return output

    def _build_operation_plan(
        self,
        data: CoordinatorInput,
        risk_level: RiskLevel,
        forecast,
        resources,
        incidents,
    ) -> CoordinatedOperationPlan:
        recommendations: list[str] = []

        event_label = data.event_name or "the event"
        recommendations.append(
            f"Maintain {risk_level.upper()} posture for {event_label} "
            f"({data.expected_attendance:,} expected / {data.venue_capacity:,} capacity)."
        )

        if data.mission_goal:
            recommendations.append(f"Primary objective: {data.mission_goal}")

        critical_zones = [z.zone for z in forecast.congestion_zones if z.level in ("high", "critical")]
        if critical_zones:
            recommendations.append(
                f"Prioritize monitoring at: {', '.join(critical_zones)}."
            )

        recommendations.append(
            f"Deploy {resources.recommended_security_staff} security, "
            f"{resources.recommended_traffic_controllers} traffic controllers, and "
            f"{resources.recommended_medical_staff} medical staff."
        )

        for action in incidents.response_actions[:6]:
            recommendations.append(f"[{action.location}] {action.action}")

        if len(incidents.response_actions) > 6:
            recommendations.append(
                f"Review {len(incidents.response_actions) - 6} additional incident actions in the ops log."
            )

        execution_steps = [
            "Read current event profile, incident records, and historical plan context from MongoDB.",
            "Forecast venue utilization, surge level, and likely congestion zones.",
            "Calculate staffing, traffic-control, and medical coverage levels for the forecast risk.",
            "Convert active incidents into prioritized field actions with clear owners.",
            "Persist the generated operation plan and tool trace for supervisor review.",
        ]

        if data.weather_condition:
            execution_steps.insert(
                2,
                f"Adjust field posture for weather condition: {data.weather_condition}.",
            )

        utilization = forecast.utilization_ratio
        success_metrics = [
            "Supervisor can approve or edit the plan before field dispatch.",
            f"Keep venue utilization below 92% of capacity during {data.time_window or 'the peak operating window'}.",
            "Reduce high-severity incident response time to under 8 minutes.",
            "Maintain a complete MongoDB audit trail for event, incident, and plan updates.",
        ]

        if utilization >= 0.92:
            success_metrics.append("Open overflow routing before crowd density crosses the critical threshold.")

        partner_tool_calls = [
            PartnerToolCall(
                tool="find",
                purpose="Load event profile and active incidents for the coordinator mission.",
                status="executed",
                collection="events, incidents",
            ),
            PartnerToolCall(
                tool="aggregate",
                purpose="Compare attendance, capacity, and incident severity signals.",
                status="executed",
                collection="events",
            ),
            PartnerToolCall(
                tool="insertOne",
                purpose="Save generated operation plan for human approval and demo replay.",
                status="planned",
                collection="operation_plans",
            ),
        ]

        return CoordinatedOperationPlan(
            risk_level=risk_level,
            recommendations=recommendations,
            mission_summary=(
                f"CrowdPilot planned a supervised multi-step response for {event_label}"
                f" at {data.venue or 'the venue'}, using MongoDB partner tools as operational memory."
            ),
            execution_steps=execution_steps,
            success_metrics=success_metrics,
            partner_tool_calls=partner_tool_calls,
        )

    async def arun(self, data: CoordinatorInput) -> CoordinatorOutput:
        return await asyncio.to_thread(self.run, data)
