from sqlalchemy import create_engine, text
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:Teradata900..@localhost:5432/weatherdb"
)

UPSERT_SQL = """ 
INSERT INTO weather_yearly_stats (
  station_id, year, avg_tmax_c, avg_tmin_c, total_prcp_cm, created_at
)
SELECT
  station_id,
  EXTRACT(YEAR FROM obs_date)::INT AS year,
  ROUND(AVG(tmax_c)::numeric, 2) AS avg_tmax_c,
  ROUND(AVG(tmin_c)::numeric, 2) AS avg_tmin_c,
  ROUND(SUM(prcp_cm)::numeric, 3) AS total_prcp_cm,
  now() AS created_at
FROM weather
GROUP BY station_id, year
ON CONFLICT (station_id, year)
  DO UPDATE SET
    avg_tmax_c = EXCLUDED.avg_tmax_c,
    avg_tmin_c = EXCLUDED.avg_tmin_c,
    total_prcp_cm = EXCLUDED.total_prcp_cm,
    created_at = EXCLUDED.created_at;
"""

def compute_and_store():
    engine = create_engine(DATABASE_URL, future=True)
    with engine.begin() as conn:
        conn.execute(text(UPSERT_SQL))
    print("Yearly stats computed and upserted.")

if __name__ == "__main__":
    compute_and_store()
