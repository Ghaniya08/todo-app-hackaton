# Research: Backend Task API & Data Layer

**Feature**: Backend Task API & Data Layer
**Branch**: `001-backend-task-api`
**Date**: 2026-02-08
**Phase**: Phase 0 - Research & Unknowns

## Overview

This document resolves all technical unknowns identified during the planning phase. Each research item includes the decision made, rationale, alternatives considered, and implementation guidance.

---

## Research Item 1: Database Connection Pooling for Neon Serverless PostgreSQL

### Question
How to configure connection pooling for Neon Serverless PostgreSQL to optimize performance while avoiding connection exhaustion?

### Research Findings

**Neon Serverless PostgreSQL Characteristics**:
- Serverless architecture with automatic scaling
- Connection pooling built-in at the platform level
- Supports both pooled and direct connections
- Pooled connection string format: `postgresql://user:pass@host/db?sslmode=require`
- Direct connection string format: `postgresql://user:pass@host/db?sslmode=require&options=project%3Dxxx`

**FastAPI + SQLModel Best Practices**:
- Use SQLAlchemy's `create_engine()` with connection pooling
- Recommended pool settings for serverless:
  - `pool_size=5` (small pool for serverless)
  - `max_overflow=10` (allow burst connections)
  - `pool_pre_ping=True` (verify connections before use)
  - `pool_recycle=3600` (recycle connections every hour)

### Decision

**Use Neon's pooled connection string with SQLAlchemy connection pooling**

**Configuration**:
```python
from sqlmodel import create_engine

engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False  # Set to True for debugging
)
```

### Rationale

- Neon's built-in pooling handles serverless scaling automatically
- SQLAlchemy pooling provides application-level connection reuse
- Small pool size (5) prevents connection exhaustion
- `pool_pre_ping` ensures stale connections are detected
- `pool_recycle` prevents long-lived connection issues

### Alternatives Considered

1. **No application-level pooling** (rely only on Neon's pooling)
   - Rejected: Would create new connections for every request, poor performance
2. **Large pool size (50+)**
   - Rejected: Wastes resources, can exhaust Neon's connection limits
3. **External pooler (PgBouncer)**
   - Rejected: Unnecessary complexity for Phase II; Neon handles this

### Implementation Guidance

- Store `DATABASE_URL` in environment variable
- Use Neon's pooled connection string (default)
- Configure engine in `backend/src/db.py`
- Create session dependency for FastAPI routes
- Close sessions properly after each request

---

## Research Item 2: Timestamp Management (SQLModel vs PostgreSQL)

### Question
Should timestamps be managed by SQLModel (Python) or PostgreSQL (database triggers)? Which approach is more reliable?

### Research Findings

**SQLModel Approach**:
- Use `datetime.utcnow()` as default value
- Managed in Python application code
- Requires explicit update on modification

**PostgreSQL Approach**:
- Use `CURRENT_TIMESTAMP` or `NOW()` as default
- Use triggers for `updated_at` (e.g., `ON UPDATE CURRENT_TIMESTAMP`)
- Managed at database level

**SQLModel + PostgreSQL Hybrid**:
- Use SQLModel's `Field(default_factory=datetime.utcnow)` for `created_at`
- Use SQLModel's `Field(sa_column_kwargs={"onupdate": datetime.utcnow})` for `updated_at`
- SQLAlchemy handles the database-level updates

### Decision

**Use SQLModel with SQLAlchemy's onupdate for timestamp management**

**Implementation**:
```python
from datetime import datetime
from sqlmodel import Field, SQLModel

class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    title: str = Field(max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow}
    )
```

### Rationale

- **Consistency**: All timestamp logic in one place (Python code)
- **Testability**: Easy to mock `datetime.utcnow()` in tests
- **Portability**: Works with any database (not PostgreSQL-specific)
- **Simplicity**: No database triggers to manage
- **SQLAlchemy Integration**: `onupdate` automatically refreshes `updated_at`

### Alternatives Considered

1. **PostgreSQL triggers**
   - Rejected: Adds database-level complexity, harder to test
2. **Manual timestamp updates in service layer**
   - Rejected: Error-prone, easy to forget, not DRY
3. **Database default values only**
   - Rejected: Doesn't handle `updated_at` automatically

### Implementation Guidance

- Use `datetime.utcnow()` for UTC timestamps (not `datetime.now()`)
- SQLAlchemy's `onupdate` triggers on any field modification
- No manual timestamp management needed in service layer
- Timestamps are set automatically by SQLModel

---

## Research Item 3: User ID Validation

### Question
Should we validate user_id format (e.g., UUID, alphanumeric) or accept any string? What are the security implications?

### Research Findings

**Security Considerations**:
- SQL injection: SQLModel/SQLAlchemy uses parameterized queries (safe)
- Path traversal: FastAPI validates path parameters (safe)
- Information disclosure: Accepting any string doesn't leak info
- Future JWT integration: JWT will contain user_id for validation

**Format Options**:
1. **No validation** - Accept any string
2. **UUID validation** - Enforce UUID format
3. **Alphanumeric validation** - Allow only letters/numbers
4. **Length validation** - Enforce min/max length

### Decision

**Accept any non-empty string for user_id with basic validation**

**Validation Rules**:
- Must not be empty
- Must not exceed 255 characters
- No format restrictions (allows UUID, email, username, etc.)

**Implementation**:
```python
from pydantic import Field, validator

class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=1000)

# Path parameter validation in route
@router.post("/api/{user_id}/tasks")
async def create_task(
    user_id: str = Path(..., min_length=1, max_length=255),
    task: TaskCreate,
    db: Session = Depends(get_db)
):
    # user_id is validated by FastAPI
    pass
```

### Rationale

- **Flexibility**: Supports various authentication systems (UUID, email, username, OAuth IDs)
- **Future-proof**: Spec 2 (JWT) will enforce user_id validation
- **Security**: SQLModel prevents SQL injection; FastAPI validates path params
- **Simplicity**: No premature optimization; validation added when needed
- **Spec Compliance**: Spec states "user_id as string" with no format requirements

### Alternatives Considered

1. **UUID-only validation**
   - Rejected: Too restrictive; Better Auth may use different formats
2. **Email validation**
   - Rejected: Assumes email-based auth; not flexible
3. **Strict alphanumeric**
   - Rejected: Breaks OAuth IDs with special characters

### Implementation Guidance

- Use FastAPI's `Path()` validator for basic checks
- Length limit (255 chars) prevents abuse
- JWT middleware (Spec 2) will validate ownership
- No regex validation needed at this stage

---

## Research Item 4: Error Response Format

### Question
What JSON structure should error responses use? Should we follow RFC 7807 (Problem Details) or a custom format?

### Research Findings

**RFC 7807 (Problem Details for HTTP APIs)**:
```json
{
  "type": "https://example.com/probs/out-of-credit",
  "title": "You do not have enough credit.",
  "detail": "Your current balance is 30, but that costs 50.",
  "instance": "/account/12345/msgs/abc",
  "status": 400
}
```

**FastAPI Default (HTTPException)**:
```json
{
  "detail": "Error message here"
}
```

**Custom Format Options**:
```json
{
  "error": "Error type",
  "message": "Human-readable message",
  "details": { "field": "error" }
}
```

### Decision

**Use FastAPI's default HTTPException format with consistent structure**

**Standard Format**:
```json
{
  "detail": "Human-readable error message"
}
```

**For validation errors** (Pydantic):
```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### Rationale

- **Simplicity**: FastAPI's built-in format, no custom middleware needed
- **Consistency**: All FastAPI apps use this format
- **Spec Compliance**: Spec requires "clear error messages" but doesn't mandate format
- **Client-friendly**: Simple structure, easy to parse
- **Validation Support**: Pydantic errors automatically formatted

### Alternatives Considered

1. **RFC 7807 (Problem Details)**
   - Rejected: Over-engineered for this project; adds complexity
2. **Custom error format**
   - Rejected: Reinventing the wheel; FastAPI's format is sufficient
3. **Nested error objects**
   - Rejected: Unnecessary complexity for simple CRUD API

### Implementation Guidance

**Standard Error Responses**:
```python
from fastapi import HTTPException

# 400 Bad Request
raise HTTPException(status_code=400, detail="Title is required")

# 404 Not Found
raise HTTPException(status_code=404, detail="Task not found")

# 500 Internal Server Error
raise HTTPException(status_code=500, detail="Service temporarily unavailable")
```

**Validation Errors** (automatic via Pydantic):
- FastAPI handles validation errors automatically
- Returns 422 Unprocessable Entity with field details
- No custom code needed

**Error Handling Middleware** (optional):
```python
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    # Log error for debugging
    logger.error(f"Unhandled error: {exc}")
    # Return generic error to user
    return JSONResponse(
        status_code=500,
        content={"detail": "Service temporarily unavailable"}
    )
```

---

## Research Item 5: Test Database Strategy

### Question
Should tests use an in-memory SQLite database or a separate Neon test database? What are the tradeoffs?

### Research Findings

**Option 1: In-Memory SQLite**
- Pros: Fast, isolated, no external dependencies
- Cons: Different SQL dialect, may not catch PostgreSQL-specific issues

**Option 2: Separate Neon Test Database**
- Pros: Same database as production, catches PostgreSQL-specific issues
- Cons: Slower, requires network, cleanup complexity

**Option 3: Docker PostgreSQL**
- Pros: Local PostgreSQL, no network dependency, same dialect
- Cons: Requires Docker, slower than SQLite

**Option 4: Hybrid Approach**
- Unit tests: SQLite (fast, isolated)
- Integration tests: PostgreSQL (realistic)

### Decision

**Use in-memory SQLite for all tests (unit, contract, integration)**

**Configuration**:
```python
# tests/conftest.py
import pytest
from sqlmodel import create_engine, Session, SQLModel
from fastapi.testclient import TestClient

SQLITE_URL = "sqlite:///:memory:"

@pytest.fixture(name="engine")
def engine_fixture():
    engine = create_engine(
        SQLITE_URL,
        connect_args={"check_same_thread": False}
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)

@pytest.fixture(name="session")
def session_fixture(engine):
    with Session(engine) as session:
        yield session

@pytest.fixture(name="client")
def client_fixture(session):
    def get_session_override():
        return session

    app.dependency_overrides[get_db] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
```

### Rationale

- **Speed**: In-memory SQLite is 10-100x faster than network databases
- **Isolation**: Each test gets a fresh database, no cleanup needed
- **Simplicity**: No external dependencies, works in CI/CD
- **SQLModel Compatibility**: SQLModel abstracts SQL dialects well
- **Good Enough**: For CRUD operations, SQLite is sufficient
- **Phase II Scope**: Advanced PostgreSQL features not needed yet

### Alternatives Considered

1. **Separate Neon test database**
   - Rejected: Slower, requires network, cleanup complexity
2. **Docker PostgreSQL**
   - Rejected: Adds Docker dependency, slower than SQLite
3. **Hybrid approach**
   - Rejected: Unnecessary complexity for Phase II

### Implementation Guidance

**Test Structure**:
```python
# tests/contract/test_task_api.py
def test_create_task(client):
    response = client.post(
        "/api/user123/tasks",
        json={"title": "Test task", "description": "Test description"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test task"
    assert data["user_id"] == "user123"
```

**Fixture Usage**:
- `engine`: Database engine (SQLite in-memory)
- `session`: Database session for direct DB access
- `client`: TestClient for API testing

**Test Isolation**:
- Each test gets a fresh database (via fixture scope)
- No manual cleanup needed
- Tests can run in parallel (pytest-xdist)

---

## Summary of Decisions

| Research Item | Decision | Rationale |
|---------------|----------|-----------|
| **Connection Pooling** | Neon pooled connection + SQLAlchemy pooling (pool_size=5) | Balances performance and resource usage |
| **Timestamp Management** | SQLModel with `default_factory` and `onupdate` | Consistent, testable, portable |
| **User ID Validation** | Accept any non-empty string (max 255 chars) | Flexible, future-proof, secure |
| **Error Response Format** | FastAPI default HTTPException format | Simple, consistent, client-friendly |
| **Test Database** | In-memory SQLite for all tests | Fast, isolated, no external dependencies |

---

## Technology Stack Finalized

**Core Dependencies**:
- `fastapi` - Web framework
- `sqlmodel` - ORM (SQLAlchemy + Pydantic)
- `psycopg2-binary` - PostgreSQL driver
- `uvicorn` - ASGI server
- `pydantic` - Data validation (included with FastAPI)
- `python-dotenv` - Environment variable management

**Testing Dependencies**:
- `pytest` - Test framework
- `pytest-asyncio` - Async test support
- `httpx` - Async HTTP client for TestClient
- `pytest-cov` - Code coverage reporting

**Development Dependencies**:
- `black` - Code formatting
- `ruff` - Linting
- `mypy` - Type checking

---

## Next Steps

1. ✅ Phase 0 Complete - All unknowns resolved
2. ➡️ Phase 1: Create `data-model.md` with Task entity definition
3. ➡️ Phase 1: Create `contracts/` with OpenAPI specification
4. ➡️ Phase 1: Create `quickstart.md` with setup instructions
5. ➡️ Phase 1: Update agent context with finalized technologies
6. ➡️ Re-evaluate Constitution Check (should still pass)
7. ➡️ Run `/sp.tasks` to generate task breakdown

---

**Research Status**: ✅ COMPLETE
**All Unknowns Resolved**: Yes
**Ready for Phase 1**: Yes
