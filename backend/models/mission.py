from pydantic import BaseModel, Field
from .incident import IncidentStatus, Severity
from datetime import datetime


class IncidentDataItem(BaseModel):
    location: str = Field(..., min_length=1)
    severity: Severity
    description: str = Field(..., min_length=1)
    status: IncidentStatus = "open"
    timestamp: datetime | None = None
    id: str | None = None


class CoordinatorInput(BaseModel):
    expected_attendance: int = Field(..., ge=0)
    venue_capacity: int = Field(..., ge=1)
    incident_data: list[IncidentDataItem] = Field(default_factory=list)
    event_name: str | None = Field(default=None, max_length=200)
    mission_goal: str | None = Field(default=None, max_length=600)
    venue: str | None = Field(default=None, max_length=200)
    weather_condition: str | None = Field(default=None, max_length=120)
    time_window: str | None = Field(default=None, max_length=120)