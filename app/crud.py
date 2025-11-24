# app/crud.py (replace get_weather and get_stats)
from typing import List, Optional, Tuple
from math import ceil
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_

from app.db.models import Weather, WeatherYearlyStats


def get_weather(
    db: Session,
    station_id: Optional[str] = None,
    date_eq: Optional[str] = None,
    page: int = 1,
    page_size: int = 100,
) -> Tuple[int, int, List[Weather]]:
    """
    Return (total_count, page_count, rows) for Weather matching filters.
    page is 1-based. page_size must be >0.
    """
    q = select(Weather)
    filters = []
    if station_id:
        filters.append(Weather.station_id == station_id)
    if date_eq:
        filters.append(Weather.obs_date == date_eq)
    if filters:
        q = q.where(and_(*filters))

    total = db.execute(select(func.count()).select_from(q.subquery())).scalar_one()
    page_size = max(1, page_size)
    page_count = ceil(total / page_size) if total else 0
    offset = (max(1, page) - 1) * page_size

    q = q.order_by(Weather.obs_date).limit(page_size).offset(offset)
    results = db.execute(q).scalars().all()
    return total, page_count, results


def get_stats(
    db: Session,
    station_id: Optional[str] = None,
    year_eq: Optional[int] = None,
    page: int = 1,
    page_size: int = 100,
) -> Tuple[int, int, List[WeatherYearlyStats]]:
    """
    Return (total_count, page_count, rows) for WeatherYearlyStats matching filters.
    """
    q = select(WeatherYearlyStats)
    filters = []
    if station_id:
        filters.append(WeatherYearlyStats.station_id == station_id)
    if year_eq:
        filters.append(WeatherYearlyStats.year == year_eq)
    if filters:
        q = q.where(and_(*filters))

    total = db.execute(select(func.count()).select_from(q.subquery())).scalar_one()
    page_size = max(1, page_size)
    page_count = ceil(total / page_size) if total else 0
    offset = (max(1, page) - 1) * page_size

    q = (
        q.order_by(WeatherYearlyStats.station_id, WeatherYearlyStats.year)
        .limit(page_size)
        .offset(offset)
    )
    results = db.execute(q).scalars().all()
    return total, page_count, results
