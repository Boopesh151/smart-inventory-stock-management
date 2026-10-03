"""Database connection and session setup.

This file is the single place that knows:
- where the SQLite file lives
- how to create the SQLAlchemy engine
- how to open a database session
- the Base class that models inherit from
"""

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Put the .db file next to this package (inside the backend folder).
# Using Path(__file__) keeps the location stable even if we start uvicorn
# from a different working directory.
BACKEND_DIR = Path(__file__).resolve().parent
DATABASE_FILE = BACKEND_DIR / "smart_inventory.db"
DATABASE_URL = f"sqlite:///{DATABASE_FILE}"

# SQLite only allows one thread to use a connection by default.
# FastAPI can use the database from different threads, so we disable
# that check. This setting is SQLite-specific.
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

# sessionmaker is a factory: call SessionLocal() whenever you need
# a new database session (one conversation with the database).
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class for all ORM models.

    Every table class (like Product) should inherit from this.
    SQLAlchemy uses it to collect table definitions and create them.
    """

    pass


def get_db():
    """Yield one database session, then close it.

    FastAPI will use this later as a dependency for CRUD routes.
    We are not wiring those routes yet; this helper is ready for them.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
