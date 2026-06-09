from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field

from models.incident import IncidentStatus, Severity
from models.operation_plan import RiskLevel

CongestionLevel = Literal["low", "moderate", "high", "critical"]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


# --- Forecast Agent ---


class ForecastInput(BaseModel):
    expected_attendance: int = Field(..., ge=0)
    venue_capacity: int = Field(..., ge=1)


class CongestionZone(BaseModel):
    zone: str
    level: CongestionLevel
    reason: str


class ForecastOutput(BaseModel):
    crowd_risk_level: RiskLevel
    utilization_ratio: float = Field(..., ge=0)
    congestion_zones: list[CongestionZone]


# --- Resource Agent ---


class ResourceInput(BaseModel):
    crowd_risk_level: RiskLevel
    expected_attendance: int | None = Field(default=None, ge=0)
    venue_capacity: int | None = Field(default=None, ge=1)
    utilization_ratio: float | None = Field(default=None, ge=0)


class ResourceOutput(BaseModel):
    recommended_security_staff: int = Field(..., ge=0)
    recommended_traffic_controllers: int = Field(..., ge=0)
    recommended_medical_staff: int = Field(..., ge=0)


# --- Incident Agent ---


class IncidentDataItem(BaseModel):
    location: str = Field(..., min_length=1)
    severity: Severity
    description: str = Field(..., min_length=1)
    status: IncidentStatus = "open"
    timestamp: datetime | None = None
    id: str | None = None


class IncidentAgentInput(BaseModel):
    incident_data: list[IncidentDataItem] = Field(default_factory=list)


class ResponseAction(BaseModel):
    incident_ref: str
    location: str
    priority: Severity
    action: str


class IncidentAgentOutput(BaseModel):
    response_actions: list[ResponseAction]


# --- Coordinator Agent ---


class CoordinatorInput(BaseModel):
    expected_attendance: int = Field(..., ge=0)
    venue_capacity: int = Field(..., ge=1)
    incident_data: list[IncidentDataItem] = Field(default_factory=list)
    event_name: str | None = Field(default=None, max_length=200)
    mission_goal: str | None = Field(
        default=None,
        max_length=600,
        description="Operator objective the agent should plan and execute toward.",
    )
    venue: str | None = Field(default=None, max_length=200)
    weather_condition: str | None = Field(default=None, max_length=120)
    time_window: str | None = Field(default=None, max_length=120)


class AgentPipelineOutputs(BaseModel):
    forecast: ForecastOutput
    resources: ResourceOutput
    incidents: IncidentAgentOutput


class PartnerToolCall(BaseModel):
    partner: str = "MongoDB"
    mcp_server: str = "mongodb/mongodb-mcp-server"
    tool: str
    purpose: str
    status: Literal["planned", "executed", "simulated"]
    collection: str | None = None


class CoordinatedOperationPlan(BaseModel):
    risk_level: RiskLevel
    recommendations: list[str]
    mission_summary: str
    execution_steps: list[str]
    success_metrics: list[str]
    partner_tool_calls: list[PartnerToolCall] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=utc_now)


class CoordinatorOutput(BaseModel):
    agents: AgentPipelineOutputs
    operation_plan: CoordinatedOperationPlan
