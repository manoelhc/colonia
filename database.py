"""Database configuration and session management."""

import os
from sqlmodel import create_engine, Session, SQLModel
from contextlib import contextmanager

# Database URL - using SQLite3 for testing (can be overridden via environment)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./colonia.db")

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    connect_args=(
        {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
    ),
    echo=False,  # Set to True for SQL query logging
)


def create_db_and_tables():
    """Create database tables."""
    SQLModel.metadata.create_all(engine)


@contextmanager
def get_session():
    """Get a database session with automatic cleanup."""
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
