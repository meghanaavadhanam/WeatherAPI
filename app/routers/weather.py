# app/routers/weather.py
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app import crud, schemas

router = APIRouter()

@router.get("/", response_model=dict)
def list_weather(
    station_id: Optional[str] = Query(None),
    date: Optional[str] = Query(None, description="YYYY-MM-DD exact date"),
    page: int = Query(1, ge=1, description="1-based page number"),
    page_size: int = Query(100, ge=1, le=1000, description="Number of items per page"),
    db: Session = Depends(get_db),
):
    total, page_count, rows = crud.get_weather(
        db,
        station_id=station_id,
        date_eq=date,
        page=page,
        page_size=page_size,
    )
    return {
        "total": total,
        "page": page,
        "page_count": page_count,
        "page_size": page_size,
        "items": [schemas.WeatherResponse.from_orm(r).dict() for r in rows],
    }
