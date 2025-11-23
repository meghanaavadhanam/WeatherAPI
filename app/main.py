# src/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import weather, stats

app = FastAPI(
    title="Weather ETL API",
    description="API exposing ingested weather records and yearly aggregated stats.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# include routers
app.include_router(weather.router, prefix="/api/weather", tags=["weather"])
app.include_router(stats.router, prefix="/api/weather/stats", tags=["weather_stats"])
