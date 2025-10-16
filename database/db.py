"""Database connection and session management."""
import os
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from config.config import config
from database.models import Base


# Ensure SQLite data directory exists if using file-based SQLite
if config.DATABASE_URL.startswith("sqlite"):
    # Extract path part after sqlite:///
    db_path = config.DATABASE_URL.replace("sqlite:///", "")
    dir_path = os.path.dirname(db_path) if "/" in db_path else "."
    if dir_path and not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)

# Create engine (handle SQLite check_same_thread)
engine_kwargs = {
    "pool_pre_ping": True,
    "echo": False,
}
if config.DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(
    config.DATABASE_URL,
    **engine_kwargs,
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """Get database session with context manager."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def get_db_session():
    """Get database session for FastAPI dependency injection."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
