from fastapi import APIRouter

from adk_agents.forecast_agent import forecast_agent
from adk_agents.incident_agent import incident_agent
from adk_agents.resource_agent import resource_agent
from adk_agents.operation_agent import operation_agent
from adk_agents.root_agent import root_agent

router = APIRouter()

@router.post("/forecast")
async def run_forecast_agent(payload: dict):
    return await forecast_agent.arun(payload)

@router.post("/resources")
async def run_resource_agent(payload: dict):
    return await resource_agent.arun(payload)

@router.post("/incidents")
async def run_incident_agent(payload: dict):
    return await incident_agent.arun(payload)

@router.post("/operation")
async def run_operation_agent(payload: dict):
    return await operation_agent.arun(payload)

@router.post("/coordinate")
async def run_root_agent(payload: dict):
    return await root_agent.arun(payload)