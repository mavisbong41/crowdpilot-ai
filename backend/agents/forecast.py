import asyncio
import json
import logging

from agents.base import BaseAgent
from agents.gemini_runner import run_with_gemini_fallback
from agents.prompts import FORECAST_SYSTEM
from agents.rule_based import run_forecast_rules
from agents.schemas import ForecastInput, ForecastOutput
from services.gemini_service import get_gemini_service

logger = logging.getLogger("crowdpilot.agents.forecast")


class ForecastAgent(BaseAgent[ForecastInput, ForecastOutput]):
    name = "forecast"

    def run(self, data: ForecastInput) -> ForecastOutput:
        return run_with_gemini_fallback(
            agent_name=self.name,
            data=data,
            gemini_call=lambda: self._run_gemini(data),
            rule_call=run_forecast_rules,
        )

    def _run_gemini(self, data: ForecastInput) -> ForecastOutput:
        user_message = json.dumps(
            {
                "expected_attendance": data.expected_attendance,
                "venue_capacity": data.venue_capacity,
                "task": "Assess crowd risk and identify congestion zones for this event.",
            },
            indent=2,
        )
        result = get_gemini_service().generate_structured(
            agent_name=self.name,
            system_instruction=FORECAST_SYSTEM,
            user_message=user_message,
            response_model=ForecastOutput,
        )
        ratio = data.expected_attendance / data.venue_capacity
        if abs(result.utilization_ratio - ratio) > 0.05:
            result = result.model_copy(update={"utilization_ratio": round(ratio, 4)})
        return result

    async def arun(self, data: ForecastInput) -> ForecastOutput:
        return await asyncio.to_thread(self.run, data)
