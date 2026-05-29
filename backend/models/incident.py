from datetime import datetime
from typing import Literal, Self

from pydantic import BaseModel, Field, field_validator, model_validator

Severity = Literal["low", "medium", "high", "critical"]
IncidentStatus = Literal["open", "acknowledged", "in_progress", "resolved", "closed"]


class IncidentBase(BaseModel):
    location: str = Field(..., min_length=1, max_length=300)
    severity: Severity
    description: str = Field(..., min_length=1, max_length=5000)
    status: IncidentStatus = "open"
    timestamp: datetime


class IncidentCreate(IncidentBase):
    pass


class IncidentUpdate(BaseModel):
    location: str | None = Field(default=None, min_length=1, max_length=300)
    severity: Severity | None = None
    description: str | None = Field(default=None, min_length=1, max_length=5000)
    status: IncidentStatus | None = None
    timestamp: datetime | None = None


class IncidentResponse(IncidentBase):
    id: str

    @field_validator("timestamp", mode="before")
    @classmethod
    def parse_timestamp(cls, value: datetime | str) -> datetime:
        if isinstance(value, datetime):
            return value
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
