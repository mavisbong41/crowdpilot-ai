from config import settings
from google.adk.agents import LlmAgent

from mcp_tools.mongodb_tool import (
    save_operation_plan
)

operation_agent = LlmAgent(
    name="operation_agent",
    model=settings.gemini_model, 
    instruction="""
You are CrowdPilot Operation Planning Agent.

Input:

Forecast Result
Incident Result
Resource Result

CRITICAL RULES:

1. Generate a final operational deployment plan.
2. MUST create mission_name.
3. MUST generate deployment actions.
4. MUST generate success criteria.
5. After generating the plan,
   MUST call save_operation_plan.
6. MongoDB MCP is the system of record.
7. Save the complete plan to MongoDB.
8. Return ONLY valid JSON.

Output:

{
  "mission_name": "",
  "priority": "",
  "objective": "",
  "actions": [],
  "deployment_summary": [],
  "success_criteria": []
}

No markdown.
No explanations.
JSON only.
""",

    tools=[
        save_operation_plan
    ]
)