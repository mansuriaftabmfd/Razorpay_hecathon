# ============================================================
# backend/database.py — Database Engine & Session Management
# ============================================================
# Provides SQLAlchemy database connection pooling, SessionLocal
# factory, declarative base, and FastAPI dependency session injection.
# ============================================================

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Path configuration for SQLite storage
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_PATH = os.path.join(PROJECT_ROOT, "returnshield.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

# SQLAlchemy engine initialization
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # Multi-threaded support for FastAPI
    echo=False,
)

# Session factory for scoped transactions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base model
Base = declarative_base()


def get_db():
    """
    FastAPI dependency injection provider for transactional database sessions.
    Automatically closes session upon request completion.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """
    Initializes and creates all relational database tables on startup.
    """
    from backend import models  # noqa: F401
    Base.metadata.create_all(bind=engine)
