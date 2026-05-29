from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field, field_validator

RiskLevel = Literal["low", "medium", "high", "critical"]


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class OperationPlanBase(BaseModel):
    risk_level: RiskLevel
    recommendations: list[str] = Field(..., min_length=1)
    generated_at: datetime = Field(default_factory=_utc_now)

    @field_validator("recommendations")
    @classmethod
    def strip_recommendations(cls, values: list[str]) -> list[str]:
        cleaned = [item.strip() for item in values if item and item.strip()]
        if not cleaned:
            raise ValueError("recommendations must contain at least one non-empty item")
        return cleaned


class OperationPlanCreate(BaseModel):
    risk_level: RiskLevel
    recommendations: list[str] = Field(..., min_length=1)
    generated_at: datetime = Field(default_factory=_utc_now)

    @field_validator("recommendations")
    @classmethod
    def strip_recommendations(cls, values: list[str]) -> list[str]:
        cleaned = [item.strip() for item in values if item and item.strip()]
        if not cleaned:
            raise ValueError("recommendations must contain at least one non-empty item")
        return cleaned


class OperationPlanUpdate(BaseModel):
    risk_level: RiskLevel | None = None
    recommendations: list[str] | None = Field(default=None, min_length=1)
    generated_at: datetime | None = None

    @field_validator("recommendations")
    @classmethod
    def strip_recommendations(cls, values: list[str] | None) -> list[str] | None:
        if values is None:
            return None
        cleaned = [item.strip() for item in values if item and item.strip()]
        if not cleaned:
            raise ValueError("recommendations must contain at least one non-empty item")
        return cleaned


class OperationPlanResponse(OperationPlanBase):
    id: str

    @field_validator("generated_at", mode="before")
    @classmethod
    def parse_generated_at(cls, value: datetime | str) -> datetime:
        if isinstance(value, datetime):
            return value
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
