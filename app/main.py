# src/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from app.routers import weather, stats
import os

app = FastAPI(
    title="Weather ETL API",
    description="API exposing ingested weather records and yearly aggregated stats.",
    version="0.1.0",
)

@app.get("/")
def root():
    return {"ok": True, "msg": "Weather API - see /docs"}

@app.get("/api/health")
def health_db():
    connstr = os.environ.get("DATABASE_URL")
    if not connstr:
        return {"ok": False, "error": "DATABASE_URL not set"}
    try:
        engine = create_engine(connstr)
        with engine.connect() as conn:
            total = conn.execute(text("select count(*) from weather")).scalar()
        return {"ok": True, "total_rows": int(total)}
    except Exception as e:
        return {"ok": False, "error": str(e)}
    
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# include routers
app.include_router(weather.router, prefix="/api/weather", tags=["weather"])
app.include_router(stats.router, prefix="/api/weather/stats", tags=["weather_stats"])
