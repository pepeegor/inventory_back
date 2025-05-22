from datetime import date
from typing import Optional
from pydantic import BaseModel

class FailureStats(BaseModel):
    total_failures: int
    avg_time_to_failure_days: Optional[float] = None

class ForecastResponse(BaseModel):
    forecast_replacement_date: date