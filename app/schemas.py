# src/app/schemas.py
from datetime import date
from typing import Optional
from pydantic import BaseModel


class WeatherBase(BaseModel):
    station_id: str
    obs_date: date
    tmax_c: Optional[float] = None
    tmin_c: Optional[float] = None
    prcp_cm: Optional[float] = None

    class Config:
        orm_mode = True


class WeatherResponse(WeatherBase):
    pass


class WeatherStatsBase(BaseModel):
    station_id: str
    year: int
    avg_tmax_c: Optional[float] = None
    avg_tmin_c: Optional[float] = None
    total_prcp_cm: Optional[float] = None

    class Config:
        orm_mode = True


class WeatherStatsResponse(WeatherStatsBase):
    pass


class PaginatedResponse(BaseModel):
    total: int
    limit: int
    offset: int
