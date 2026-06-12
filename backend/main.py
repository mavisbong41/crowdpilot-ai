from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from adk_agents.exceptions import AgentError, GeminiServiceError
from config import settings
from logging_config import setup_logging
from database.connection import close_db, connect_db
from routes import events, health, incidents, missions, plans, agents

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    yield
    await close_db()

app = FastAPI(
    title="CrowdPilot AI",
    description="Event operations platform API",
    version="0.4.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


@app.exception_handler(GeminiServiceError)
async def gemini_exception_handler(_request, exc: GeminiServiceError):
    return JSONResponse(
        status_code=503,
        content={"detail": str(exc), "error_type": "gemini_service_error"},
    )


@app.exception_handler(AgentError)
async def agent_exception_handler(_request, exc: AgentError):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "error_type": "agent_error"},
    )


app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(events.router, prefix="/api/events", tags=["events"])
app.include_router(incidents.router, prefix="/api/incidents", tags=["incidents"])
app.include_router(plans.router, prefix="/api/plans", tags=["operation_plans"])
app.include_router(missions.router, prefix="/api/mission", tags=["missions"])
app.include_router(agents.router, prefix="/api/agents", tags=["agents"])