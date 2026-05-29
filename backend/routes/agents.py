from fastapi import APIRouter

from agents.coordinator import CoordinatorAgent
from agents.forecast import ForecastAgent
from agents.incident import IncidentAgent
from agents.resource import ResourceAgent
from agents.schemas import (
    CoordinatorInput,
    CoordinatorOutput,
    ForecastInput,
    ForecastOutput,
    IncidentAgentInput,
    IncidentAgentOutput,
    ResourceInput,
    ResourceOutput,
)
from models.operation_plan import OperationPlanResponse
from services.orchestrator import OrchestratorService

router = APIRouter()

forecast_agent = ForecastAgent()
resource_agent = ResourceAgent()
incident_agent = IncidentAgent()
coordinator_agent = CoordinatorAgent()
orchestrator = OrchestratorService(coordinator=coordinator_agent)


@router.post("/forecast", response_model=ForecastOutput)
async def run_forecast_agent(payload: ForecastInput):
    """Run ForecastAgent independently."""
    return await forecast_agent.arun(payload)


@router.post("/resources", response_model=ResourceOutput)
async def run_resource_agent(payload: ResourceInput):
    """Run ResourceAgent independently."""
    return await resource_agent.arun(payload)


@router.post("/incidents", response_model=IncidentAgentOutput)
async def run_incident_agent(payload: IncidentAgentInput):
    """Run IncidentAgent independently."""
    return await incident_agent.arun(payload)


@router.post("/coordinate", response_model=CoordinatorOutput)
async def run_coordinator(payload: CoordinatorInput):
    """Run full multi-agent workflow via CoordinatorAgent."""
    return await coordinator_agent.arun(payload)


@router.post("/coordinate/save", response_model=dict)
async def run_coordinator_and_save(payload: CoordinatorInput):
    """Run coordinator workflow and persist the operation plan to MongoDB."""
    result, saved_plan = await orchestrator.run_and_save(payload)
    return {
        "pipeline": result.model_dump(mode="json"),
        "saved_plan": saved_plan.model_dump(mode="json"),
    }
