# app/db/models.py
from sqlalchemy import (
    Column,
    Integer,
    BigInteger,
    String,
    Date,
    DateTime,
    Float,
    func,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Station(Base):
    __tablename__ = "stations"

    station_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=True)
    state = Column(String(2), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Weather(Base):
    __tablename__ = "weather"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    station_id = Column(String, nullable=False, index=True)
    obs_date = Column(Date, nullable=False, index=True)

    # raw values (as in files)
    tmax_raw = Column(Integer, nullable=True)
    tmin_raw = Column(Integer, nullable=True)
    prcp_raw = Column(Integer, nullable=True)

    # normalized/cleaned values
    tmax_c = Column(Float, nullable=True)
    tmin_c = Column(Float, nullable=True)
    prcp_cm = Column(Float, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("station_id", "obs_date", name="uniq_station_date"),
    )


class WeatherYearlyStats(Base):
    __tablename__ = "weather_yearly_stats"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    station_id = Column(String, nullable=False, index=True)
    year = Column(Integer, nullable=False, index=True)

    avg_tmax_c = Column(Float, nullable=True)
    avg_tmin_c = Column(Float, nullable=True)
    total_prcp_cm = Column(Float, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("station_id", "year", name="uniq_stats_station_year"),
    )
