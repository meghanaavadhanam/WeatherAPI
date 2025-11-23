# app/db/create_db.py
import os
from sqlalchemy import create_engine
from app.db.models import Base


DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+psycopg2://postgres:Teradata900..@localhost:5432/weatherdb"
)


def create_tables():
    engine = create_engine(DATABASE_URL, echo=False, future=True)
    Base.metadata.create_all(engine)
    print("Tables created (or already exist).")


if __name__ == "__main__":
    create_tables()
