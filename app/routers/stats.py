# app/routers/stats.py
from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app import crud, schemas

router = APIRouter()


@router.get("/", response_model=dict)
def list_stats(
    station_id: Optional[str] = Query(None),
    year: Optional[int] = Query(None),
    page: int = Query(1, ge=1, description="1-based page number"),
    page_size: int = Query(100, ge=1, le=1000, description="Number of items per page"),
    db: Session = Depends(get_db),
):
    total, page_count, rows = crud.get_stats(
        db, station_id=station_id, year_eq=year, page=page, page_size=page_size
    )
    return {
        "total": total,
        "page": page,
        "page_count": page_count,
        "page_size": page_size,
        "items": [schemas.WeatherStatsResponse.from_orm(r).dict() for r in rows],
    }
