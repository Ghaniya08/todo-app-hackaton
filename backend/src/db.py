"""
Database connection and session management for Backend Task API.

[Task]: T007, T040
[From]: specs/001-backend-task-api/plan.md §Technical Context
[From]: specs/001-backend-task-api/research.md §Research Item 1 (Connection Pooling)
"""

import logging
from sqlmodel import create_engine, Session, SQLModel
from .config import settings

# Initialize logger
logger = logging.getLogger(__name__)

# Create database engine with connection pooling
# Settings from research.md: pool_size=5, max_overflow=10, pool_pre_ping=True, pool_recycle=3600
engine = create_engine(
    settings.database_url,
    pool_size=5,  # Small pool for serverless
    max_overflow=10,  # Allow burst connections
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=3600,  # Recycle connections every hour
    echo=settings.is_development,  # Log SQL in development
)

# Log database connection info
logger.info(f"Database engine created with pool_size=5, max_overflow=10")


def init_db():
    """
    Initialize database by creating all tables.

    This should be called on application startup.
    Uses SQLModel.metadata.create_all() to create tables.
    """
    logger.info("Initializing database schema")
    SQLModel.metadata.create_all(engine)
    logger.info("Database schema initialized successfully")


def get_session():
    """
    Dependency function to get database session.

    Yields:
        Session: SQLModel database session

    Usage:
        @app.get("/endpoint")
        def endpoint(session: Session = Depends(get_session)):
            # Use session here
            pass
    """
    with Session(engine) as session:
        yield session
