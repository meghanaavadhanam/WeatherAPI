# app/db/create_db.py
import os
from sqlalchemy import create_engine
from app.db.models import Base
from app.db.models import Weather, WeatherYearlyStats

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is missing! Set it in your environment.")


def create_tables():
    engine = create_engine(DATABASE_URL, echo=False, future=True)
    Base.metadata.create_all(engine)
    print("Tables created (or already exist).")


if __name__ == "__main__":
    create_tables()
