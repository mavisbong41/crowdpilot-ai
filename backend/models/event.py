from datetime import date
from typing import Self

from pydantic import BaseModel, Field, field_validator, model_validator

from models.common import WeatherInfo


class EventBase(BaseModel):
    event_name: str = Field(..., min_length=1, max_length=200)
    venue: str = Field(..., min_length=1, max_length=300)
    expected_attendance: int = Field(..., ge=0, le=5_000_000)
    venue_capacity: int = Field(..., ge=1, le=5_000_000)
    event_date: date
    weather: WeatherInfo


class EventCreate(EventBase):
    @model_validator(mode="after")
    def attendance_within_capacity(self) -> Self:
        if self.expected_attendance > self.venue_capacity:
            raise ValueError("expected_attendance cannot exceed venue_capacity")
        return self


class EventUpdate(BaseModel):
    event_name: str | None = Field(default=None, min_length=1, max_length=200)
    venue: str | None = Field(default=None, min_length=1, max_length=300)
    expected_attendance: int | None = Field(default=None, ge=0, le=5_000_000)
    venue_capacity: int | None = Field(default=None, ge=1, le=5_000_000)
    event_date: date | None = None
    weather: WeatherInfo | None = None

    @model_validator(mode="after")
    def validate_capacity(self) -> Self:
        if (
            self.expected_attendance is not None
            and self.venue_capacity is not None
            and self.expected_attendance > self.venue_capacity
        ):
            raise ValueError("expected_attendance cannot exceed venue_capacity")
        return self


class EventResponse(EventBase):
    id: str

    @field_validator("event_date", mode="before")
    @classmethod
    def parse_event_date(cls, value: date | str) -> date:
        if isinstance(value, date):
            return value
        return date.fromisoformat(str(value)[:10])
