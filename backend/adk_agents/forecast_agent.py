from config import settings
from google.adk.agents import LlmAgent

from mcp_tools.mongodb_tool import get_historical_events


forecast_agent = LlmAgent(
    name="forecast_agent",
    model=settings.gemini_model, 
    instruction="""
You are CrowdPilot Forecast Agent.

CRITICAL RULES:

1. You MUST call get_historical_events.
2. Analyze historical events.
3. Compare attendance patterns.

Return ONLY valid JSON.

{
  "risk_level": "",
  "utilization_ratio": 0.0,
  "attendance": 0,
  "capacity": 0,
  "congestion_zones": [],
  "historical_events_analyzed": 0,
  "recommended_monitoring_zones": []
}

No explanation.
JSON only.
""",
    tools=[
        get_historical_events,
    ],
)