# tests/test_models.py
from app.db.models import Weather


def test_weather_has_fields():
    assert hasattr(Weather, "station_id")
