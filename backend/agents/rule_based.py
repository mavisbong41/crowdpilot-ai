"""Rule-based agent implementations used as fallback when Gemini is unavailable."""

from agents.schemas import (
    CongestionLevel,
    CongestionZone,
    ForecastInput,
    ForecastOutput,
    IncidentAgentInput,
    IncidentAgentOutput,
    IncidentDataItem,
    ResourceInput,
    ResourceOutput,
    ResponseAction,
)
from models.operation_plan import RiskLevel

_UTILIZATION_THRESHOLDS: list[tuple[float, RiskLevel]] = [
    (0.95, "critical"),
    (0.85, "high"),
    (0.70, "medium"),
    (0.0, "low"),
]

_DEFAULT_ZONES = [
    ("main_entrance", "Primary ingress and queue management"),
    ("stage_front", "Highest density near focal point"),
    ("food_court", "Secondary gathering and line formation"),
    ("exit_corridors", "Egress bottlenecks during peak departure"),
]

_STAFFING_TABLE: dict[RiskLevel, tuple[int, int, int]] = {
    "low": (12, 6, 4),
    "medium": (24, 12, 8),
    "high": (40, 20, 14),
    "critical": (60, 32, 22),
}


def run_forecast_rules(data: ForecastInput) -> ForecastOutput:
    ratio = data.expected_attendance / data.venue_capacity
    risk_level = _risk_from_utilization(ratio)
    zones = _build_congestion_zones(ratio, risk_level, data)
    return ForecastOutput(
        crowd_risk_level=risk_level,
        utilization_ratio=round(ratio, 4),
        congestion_zones=zones,
    )


def run_resource_rules(data: ResourceInput) -> ResourceOutput:
    security, traffic, medical = _STAFFING_TABLE[data.crowd_risk_level]
    return ResourceOutput(
        recommended_security_staff=security,
        recommended_traffic_controllers=traffic,
        recommended_medical_staff=medical,
    )


def run_incident_rules(data: IncidentAgentInput) -> IncidentAgentOutput:
    if not data.incident_data:
        return IncidentAgentOutput(
            response_actions=[
                ResponseAction(
                    incident_ref="none",
                    location="venue_wide",
                    priority="low",
                    action="No active incidents reported. Maintain standard monitoring posture.",
                )
            ]
        )

    actions: list[ResponseAction] = []
    for index, incident in enumerate(data.incident_data):
        actions.extend(_actions_for_incident(incident, index))
    return IncidentAgentOutput(response_actions=actions)


def _risk_from_utilization(ratio: float) -> RiskLevel:
    for threshold, level in _UTILIZATION_THRESHOLDS:
        if ratio >= threshold:
            return level
    return "low"


def _zone_level(ratio: float, zone_weight: float) -> CongestionLevel:
    effective = min(1.0, ratio * zone_weight)
    if effective >= 0.95:
        return "critical"
    if effective >= 0.82:
        return "high"
    if effective >= 0.65:
        return "moderate"
    return "low"


def _build_congestion_zones(
    ratio: float,
    risk_level: RiskLevel,
    data: ForecastInput,
) -> list[CongestionZone]:
    weights = {
        "main_entrance": 1.1,
        "stage_front": 1.15,
        "food_court": 0.95,
        "exit_corridors": 1.05,
    }
    zones: list[CongestionZone] = []

    for zone_name, base_reason in _DEFAULT_ZONES:
        level = _zone_level(ratio, weights[zone_name])
        if ratio >= 0.85 and zone_name in ("main_entrance", "stage_front"):
            level = "critical" if risk_level == "critical" else "high"

        zones.append(
            CongestionZone(
                zone=zone_name,
                level=level,
                reason=(
                    f"{base_reason}. "
                    f"Projected fill {data.expected_attendance:,} / "
                    f"{data.venue_capacity:,} ({ratio:.0%})."
                ),
            )
        )

    if ratio > 1.0:
        zones.append(
            CongestionZone(
                zone="overflow_perimeter",
                level="critical",
                reason="Forecast attendance exceeds venue capacity; activate overflow protocol.",
            )
        )

    return zones


def _actions_for_incident(incident: IncidentDataItem, index: int) -> list[ResponseAction]:
    ref = incident.id or f"incident-{index + 1}"
    severity = incident.severity
    text = incident.description.lower()

    if "crowd" in text or "queue" in text:
        action = "Throttle entry and deploy queue marshals at location."
    elif "medical" in text or "heat" in text:
        action = "Dispatch medical team and establish cooling/hydration support."
    else:
        action = f"Assign supervisor to assess: {incident.description[:120]}"

    return [
        ResponseAction(
            incident_ref=ref,
            location=incident.location,
            priority=severity,
            action=action,
        )
    ]
