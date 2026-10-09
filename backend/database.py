
"""Database connection and session setup."""

import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

BACKEND_DIR = Path(__file__).resolve().parent
DATABASE_FILE = BACKEND_DIR / "smart_inventory.db"

# Use PostgreSQL on Render; use SQLite locally.
database_url = os.getenv("DATABASE_URL")

if database_url:
    # Normalize Render's PostgreSQL URL for the psycopg driver.
    if database_url.startswith("postgres://"):
        database_url = database_url.replace(
            "postgres://",
            "postgresql+psycopg://",
            1,
        )
    elif database_url.startswith("postgresql://"):
        database_url = database_url.replace(
            "postgresql://",
            "postgresql+psycopg://",
            1,
        )

    engine = create_engine(database_url, pool_pre_ping=True)
else:
    database_url = f"sqlite:///{DATABASE_FILE}"
    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False},
    )

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass


def get_db():
    """Provide a database session and close it afterward."""

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
