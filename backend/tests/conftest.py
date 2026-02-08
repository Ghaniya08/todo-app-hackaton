"""
Pytest fixtures for Backend Task API tests.

[Task]: T011, T012
[From]: specs/001-backend-task-api/research.md §Research Item 5 (Test Database Strategy)
[From]: specs/002-auth-jwt/plan.md §Phase 2 - Testing Infrastructure
"""

import pytest
from sqlmodel import create_engine, Session, SQLModel
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from passlib.context import CryptContext

from src.main import app
from src.db import get_session
from src.models.user import User
from src.models.task import Task  # Import Task model for table creation
from src.middleware.jwt_auth import create_jwt_token

# SQLite in-memory database for tests (from research.md)
# Use StaticPool to ensure all connections share the same in-memory database
SQLITE_URL = "sqlite:///:memory:"

# Password hashing context for test users
# [Task]: T012 - Use bcrypt with cost factor 12
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)


@pytest.fixture(name="engine")
def engine_fixture():
    """
    Create in-memory SQLite engine for tests.

    Uses StaticPool to ensure all connections share the same in-memory database.
    This is critical for SQLite :memory: databases in tests.

    Yields:
        Engine: SQLModel engine with in-memory SQLite database
    """
    # Ensure models are imported before creating tables
    # This forces SQLModel to register all table models
    from src.models import User, Task

    engine = create_engine(
        SQLITE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # Critical: ensures all connections share same in-memory DB
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="session")
def session_fixture(engine):
    """
    Create database session for tests.

    Args:
        engine: SQLModel engine fixture

    Yields:
        Session: Database session for test
    """
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session):
    """
    Create FastAPI test client with database session override.

    Args:
        session: Database session fixture

    Yields:
        TestClient: FastAPI test client
    """

    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="test_user")
def test_user_fixture(session):
    """
    Create a test user in the database.

    [Task]: T012
    [From]: specs/002-auth-jwt/data-model.md §Testing Data

    Args:
        session: Database session fixture

    Returns:
        User: Test user with known credentials
    """
    # Create test user with hashed password
    test_user = User(
        id="test-user-uuid-12345",
        email="testuser@example.com",
        password_hash=pwd_context.hash("testpassword123"),
        name="Test User",
    )
    session.add(test_user)
    session.commit()
    session.refresh(test_user)
    return test_user


@pytest.fixture(name="test_jwt_token")
def test_jwt_token_fixture(test_user):
    """
    Generate a valid JWT token for the test user.

    [Task]: T012
    [From]: specs/002-auth-jwt/plan.md §JWT Token Generation

    Args:
        test_user: Test user fixture

    Returns:
        str: Valid JWT token for test user (24 hour expiration)
    """
    return create_jwt_token(test_user.id, expires_in_hours=24)


@pytest.fixture(name="authenticated_client")
def authenticated_client_fixture(client, test_jwt_token):
    """
    Create FastAPI test client with JWT token in Authorization header.

    [Task]: T012
    [From]: specs/002-auth-jwt/plan.md §Testing Infrastructure

    Args:
        client: FastAPI test client fixture
        test_jwt_token: Valid JWT token fixture

    Returns:
        TestClient: Test client with authentication headers configured
    """
    # Add Authorization header with Bearer token
    client.headers["Authorization"] = f"Bearer {test_jwt_token}"
    return client
