import asyncio
import json
import logging

from agents.base import BaseAgent
from agents.gemini_runner import run_with_gemini_fallback
from agents.prompts import RESOURCE_SYSTEM
from agents.rule_based import run_resource_rules
from agents.schemas import ResourceInput, ResourceOutput
from services.gemini_service import get_gemini_service

logger = logging.getLogger("crowdpilot.agents.resource")


class ResourceAgent(BaseAgent[ResourceInput, ResourceOutput]):
    name = "resource"

    def run(self, data: ResourceInput) -> ResourceOutput:
        return run_with_gemini_fallback(
            agent_name=self.name,
            data=data,
            gemini_call=lambda: self._run_gemini(data),
            rule_call=run_resource_rules,
        )

    def _run_gemini(self, data: ResourceInput) -> ResourceOutput:
        payload = {
            "crowd_risk_level": data.crowd_risk_level,
            "task": "Recommend security, traffic control, and medical staffing levels.",
        }
        if data.expected_attendance is not None:
            payload["expected_attendance"] = data.expected_attendance
        if data.venue_capacity is not None:
            payload["venue_capacity"] = data.venue_capacity
        if data.utilization_ratio is not None:
            payload["utilization_ratio"] = data.utilization_ratio

        return get_gemini_service().generate_structured(
            agent_name=self.name,
            system_instruction=RESOURCE_SYSTEM,
            user_message=json.dumps(payload, indent=2),
            response_model=ResourceOutput,
        )

    async def arun(self, data: ResourceInput) -> ResourceOutput:
        return await asyncio.to_thread(self.run, data)
