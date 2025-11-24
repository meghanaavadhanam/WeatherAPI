# app/ingest.py
import os
import argparse
import tempfile
import logging
import zipfile
import boto3
from pathlib import Path
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load env variables
load_dotenv()

DEFAULT_DB_URL = os.getenv("DATABASE_URL")
if not DEFAULT_DB_URL:
    raise ValueError("DATABASE_URL missing! Define it in your .env file.")

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-2")
S3_BUCKET = os.getenv("S3_BUCKET")
S3_KEY = os.getenv("S3_KEY")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("ingest")

print(">>> PYTHON INGEST DB:", DEFAULT_DB_URL)
# NEW — download from S3 & extract
def download_and_extract_from_s3(target_dir: str):
    if os.path.exists(target_dir) and any(Path(target_dir).glob("*.txt")):
        logger.info(f"Data already exists in {target_dir}, skipping S3 download.")
        return

    if not S3_BUCKET or not S3_KEY:
        raise ValueError("S3_BUCKET or S3_KEY env variables missing.")

    logger.info(f"Downloading {S3_KEY} from S3 bucket: {S3_BUCKET}")

    s3 = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name=AWS_REGION,
    )

    zip_path = os.path.join(target_dir, "wx_data.zip")
    os.makedirs(target_dir, exist_ok=True)

    s3.download_file(S3_BUCKET, S3_KEY, zip_path)
    logger.info("Download complete. Extracting zip...")

    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(target_dir)

    os.remove(zip_path)
    logger.info("Extraction complete.")


def combine_files(data_dir: str, tmpfile: str):
    data_path = Path(data_dir)
    with open(tmpfile, "w", encoding="utf-8") as out:
        for p in sorted(data_path.glob("*.txt")):
            sid = p.stem
            with p.open("r", encoding="utf-8") as fh:
                for line in fh:
                    out.write(f"{sid}\t{line.strip()}\n")


def run_sql(engine, sql_text: str):
    with engine.begin() as conn:
        conn.execute(text(sql_text))


def copy_into_staging(engine, tmpfile_path: str):
    raw = engine.raw_connection()
    try:
        cur = raw.cursor()
        with open(tmpfile_path, "r", encoding="utf-8") as f:
            cur.copy_expert(
                "COPY weather_staging (station_id, obs_date_raw, tmax_raw, tmin_raw, prcp_raw) "
                "FROM STDIN WITH (FORMAT csv, DELIMITER E'\t')",
                f,
            )
        raw.commit()
    finally:
        raw.close()


UPSERT_SQL = """
INSERT INTO weather (station_id, obs_date, tmax_raw, tmin_raw, prcp_raw, tmax_c, tmin_c, prcp_cm, created_at)
SELECT
  station_id,
  to_date(obs_date_raw, 'YYYYMMDD') AS obs_date,
  NULLIF(tmax_raw, -9999) AS tmax_raw,
  NULLIF(tmin_raw, -9999) AS tmin_raw,
  NULLIF(prcp_raw, -9999) AS prcp_raw,
  CASE WHEN tmax_raw = -9999 THEN NULL ELSE (tmax_raw::double precision / 10.0) END AS tmax_c,
  CASE WHEN tmin_raw = -9999 THEN NULL ELSE (tmin_raw::double precision / 10.0) END AS tmin_c,
  CASE WHEN prcp_raw = -9999 THEN NULL ELSE (prcp_raw::double precision / 100.0) END AS prcp_cm,
  now() AS created_at
FROM weather_staging
ON CONFLICT (station_id, obs_date) DO UPDATE
  SET tmax_raw = EXCLUDED.tmax_raw,
      tmin_raw = EXCLUDED.tmin_raw,
      prcp_raw = EXCLUDED.prcp_raw,
      tmax_c = EXCLUDED.tmax_c,
      tmin_c = EXCLUDED.tmin_c,
      prcp_cm = EXCLUDED.prcp_cm,
      created_at = EXCLUDED.created_at;
"""


def fast_ingest(data_dir: str, db_url: str):
    # NEW: Download from S3
    download_and_extract_from_s3(data_dir)

    engine = create_engine(db_url)
    print("Creating/truncating staging table...")
    run_sql(
        engine,
        """
    CREATE TABLE IF NOT EXISTS weather_staging (
      station_id TEXT NOT NULL,
      obs_date_raw TEXT NOT NULL,
      tmax_raw INTEGER,
      tmin_raw INTEGER,
      prcp_raw INTEGER
    );
    TRUNCATE weather_staging;
    """,
    )

    with tempfile.NamedTemporaryFile(delete=False, mode="w", encoding="utf-8") as tmp:
        tmpfile = tmp.name

    print("Combining files...")
    combine_files(data_dir, tmpfile)

    print("COPYing into staging...")
    copy_into_staging(engine, tmpfile)

    print("Running upsert...")
    run_sql(engine, UPSERT_SQL)

    print("Truncating staging...")
    run_sql(engine, "TRUNCATE weather_staging;")

    os.remove(tmpfile)
    print("fast ingest done.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default="/tmp/wx_data", help="path to wx files")
    parser.add_argument("--db-url", default=DEFAULT_DB_URL)
    args = parser.parse_args()
    fast_ingest(args.data_dir, args.db_url)
