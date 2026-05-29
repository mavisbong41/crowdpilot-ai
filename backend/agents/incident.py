import asyncio
import json
import logging

from agents.base import BaseAgent
from agents.gemini_runner import run_with_gemini_fallback
from agents.prompts import INCIDENT_SYSTEM
from agents.rule_based import run_incident_rules
from agents.schemas import IncidentAgentInput, IncidentAgentOutput
from services.gemini_service import get_gemini_service

logger = logging.getLogger("crowdpilot.agents.incident")


class IncidentAgent(BaseAgent[IncidentAgentInput, IncidentAgentOutput]):
    name = "incident"

    def run(self, data: IncidentAgentInput) -> IncidentAgentOutput:
        return run_with_gemini_fallback(
            agent_name=self.name,
            data=data,
            gemini_call=lambda: self._run_gemini(data),
            rule_call=run_incident_rules,
        )

    def _run_gemini(self, data: IncidentAgentInput) -> IncidentAgentOutput:
        incidents = [
            item.model_dump(mode="json") for item in data.incident_data
        ]
        user_message = json.dumps(
            {
                "incident_data": incidents,
                "task": "Produce contingency response_actions for each incident.",
            },
            indent=2,
        )
        return get_gemini_service().generate_structured(
            agent_name=self.name,
            system_instruction=INCIDENT_SYSTEM,
            user_message=user_message,
            response_model=IncidentAgentOutput,
        )

    async def arun(self, data: IncidentAgentInput) -> IncidentAgentOutput:
        return await asyncio.to_thread(self.run, data)
