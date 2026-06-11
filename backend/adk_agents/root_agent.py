from google.adk.agents import SequentialAgent

from .forecast_agent import forecast_agent
from .incident_agent import incident_agent
from .resource_agent import resource_agent
from .operation_agent import operation_agent

root_agent = SequentialAgent(
    name="crowdpilot_root",
    sub_agents=[
        forecast_agent,
        incident_agent,
        resource_agent,
        operation_agent,
    ],
)