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

        return CoordinatedOperationPlan(
            risk_level=risk_level,
            recommendations=recommendations,
        )

    async def arun(self, data: CoordinatorInput) -> CoordinatorOutput:
        return await asyncio.to_thread(self.run, data)
