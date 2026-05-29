from pydantic import BaseModel, Field


class WeatherInfo(BaseModel):
    condition: str = Field(..., min_length=1, max_length=100)
    temperature_c: float | None = Field(default=None, ge=-60, le=60)
    precipitation_chance: float | None = Field(default=None, ge=0, le=100)
