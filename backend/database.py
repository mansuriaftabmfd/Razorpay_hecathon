# backend/database.py
# ============================================================
# DATABASE ENGINE — SQLite for dev, PostgreSQL for production
# ============================================================
# SQLite use karte hain: zero config, file-based, no server needed.
# Phase 2 ko start karne ke liye developer-friendly approach.
# ============================================================

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Project root se data directory ka path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_PATH = os.path.join(PROJECT_ROOT, "returnshield.db")

# SQLite: file-based local database (no installation needed)
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Engine banao: connect_args sirf SQLite ke liye zaroori hai
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # FastAPI multi-thread ke liye
    echo=False,  # SQL queries log nahi hongi (True karo debug ke liye)
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ORM base class
Base = declarative_base()


def get_db():
    """
    FastAPI dependency injection ke liye database session generator.
    Har request ke baad session automatically close hota hai.

    Usage in route:
        @app.get("/api/something")
        def my_route(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """
    Sab ORM models ke tables database mein create karo.
    main.py startup event mein call hota hai.
    """
    from backend import models  # circular import avoid karne ke liye
    Base.metadata.create_all(bind=engine)
