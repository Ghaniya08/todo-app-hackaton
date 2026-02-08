# Quickstart Guide: Backend Task API

**Feature**: Backend Task API & Data Layer
**Branch**: `001-backend-task-api`
**Date**: 2026-02-08

## Overview

This guide provides step-by-step instructions to set up, run, and test the Backend Task API locally.

---

## Prerequisites

### Required Software
- **Python**: 3.13 or higher
- **pip**: Latest version (comes with Python)
- **Git**: For version control
- **Neon Account**: Free account at [neon.tech](https://neon.tech)

### Optional Tools
- **curl**: For testing API endpoints (or use Postman/Insomnia)
- **PostgreSQL client**: For direct database inspection (optional)

---

## Step 1: Clone Repository

```bash
git clone https://github.com/your-repo/todo-full-stack-web-application.git
cd todo-full-stack-web-application
git checkout 001-backend-task-api
```

---

## Step 2: Set Up Python Environment

### Create Virtual Environment

**Linux/macOS**:
```bash
cd backend
python3.13 -m venv venv
source venv/bin/activate
```

**Windows**:
```bash
cd backend
python -m venv venv
venv\Scripts\activate
```

### Verify Python Version
```bash
python --version
# Should output: Python 3.13.x
```

---

## Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Core Dependencies Installed
- `fastapi` - Web framework
- `sqlmodel` - ORM (SQLAlchemy + Pydantic)
- `psycopg2-binary` - PostgreSQL driver
- `uvicorn` - ASGI server
- `python-dotenv` - Environment variable management

### Testing Dependencies
- `pytest` - Test framework
- `pytest-asyncio` - Async test support
- `httpx` - Async HTTP client
- `pytest-cov` - Code coverage

---

## Step 4: Set Up Neon Database

### Create Neon Project

1. Go to [neon.tech](https://neon.tech) and sign up (free tier)
2. Create a new project: "todo-backend"
3. Create a database: "todo_db"
4. Copy the connection string (pooled connection)

**Connection String Format**:
```
postgresql://user:password@host/database?sslmode=require
```

### Configure Environment Variables

Create `.env` file in `backend/` directory:

```bash
# backend/.env
DATABASE_URL=postgresql://user:password@host/database?sslmode=require
ENVIRONMENT=development
LOG_LEVEL=debug
```

**Important**: Never commit `.env` to version control!

### Verify Connection

```bash
# Test database connection (optional)
python -c "from sqlmodel import create_engine; engine = create_engine('YOUR_DATABASE_URL'); print('Connection successful!')"
```

---

## Step 5: Initialize Database

The database schema is created automatically on first run.

```bash
# Run the initialization script (if provided)
python src/db.py

# Or start the server (it will create tables automatically)
uvicorn src.main:app --reload
```

**Expected Output**:
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

---

## Step 6: Run the Server

### Development Mode (with auto-reload)

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Options**:
- `--reload`: Auto-restart on code changes
- `--host 0.0.0.0`: Accept connections from any IP (use `127.0.0.1` for localhost only)
- `--port 8000`: Port number (default: 8000)

### Production Mode

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Options**:
- `--workers 4`: Run 4 worker processes (adjust based on CPU cores)
- No `--reload`: Optimized for production

---

## Step 7: Test the API

### Health Check

```bash
curl http://localhost:8000/health
```

**Expected Response**:
```json
{
  "status": "healthy",
  "database": "connected"
}
```

### Create a Task (POST)

```bash
curl -X POST http://localhost:8000/api/user123/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries",
    "description": "Milk, eggs, bread"
  }'
```

**Expected Response** (201 Created):
```json
{
  "id": 1,
  "user_id": "user123",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "created_at": "2026-02-08T14:30:00Z",
  "updated_at": "2026-02-08T14:30:00Z"
}
```

### List All Tasks (GET)

```bash
curl http://localhost:8000/api/user123/tasks
```

**Expected Response** (200 OK):
```json
[
  {
    "id": 1,
    "user_id": "user123",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": false,
    "created_at": "2026-02-08T14:30:00Z",
    "updated_at": "2026-02-08T14:30:00Z"
  }
]
```

### Get Specific Task (GET)

```bash
curl http://localhost:8000/api/user123/tasks/1
```

**Expected Response** (200 OK):
```json
{
  "id": 1,
  "user_id": "user123",
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "completed": false,
  "created_at": "2026-02-08T14:30:00Z",
  "updated_at": "2026-02-08T14:30:00Z"
}
```

### Update Task (PUT)

```bash
curl -X PUT http://localhost:8000/api/user123/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries and supplies",
    "description": "Milk, eggs, bread, cleaning supplies"
  }'
```

**Expected Response** (200 OK):
```json
{
  "id": 1,
  "user_id": "user123",
  "title": "Buy groceries and supplies",
  "description": "Milk, eggs, bread, cleaning supplies",
  "completed": false,
  "created_at": "2026-02-08T14:30:00Z",
  "updated_at": "2026-02-08T15:45:00Z"
}
```

### Toggle Completion (PATCH)

```bash
curl -X PATCH http://localhost:8000/api/user123/tasks/1/complete
```

**Expected Response** (200 OK):
```json
{
  "id": 1,
  "user_id": "user123",
  "title": "Buy groceries and supplies",
  "description": "Milk, eggs, bread, cleaning supplies",
  "completed": true,
  "created_at": "2026-02-08T14:30:00Z",
  "updated_at": "2026-02-08T16:00:00Z"
}
```

### Delete Task (DELETE)

```bash
curl -X DELETE http://localhost:8000/api/user123/tasks/1
```

**Expected Response** (204 No Content):
```
(empty response body)
```

---

## Step 8: Run Tests

### Run All Tests

```bash
pytest
```

**Expected Output**:
```
======================== test session starts =========================
collected 24 items

tests/contract/test_task_api.py ................          [ 66%]
tests/integration/test_user_stories.py ......             [ 91%]
tests/unit/test_task_service.py ..                        [100%]

======================== 24 passed in 2.34s ==========================
```

### Run Specific Test Suite

```bash
# Contract tests only
pytest tests/contract/

# Integration tests only
pytest tests/integration/

# Unit tests only
pytest tests/unit/
```

### Run with Coverage Report

```bash
pytest --cov=src --cov-report=html
```

**View Coverage Report**:
```bash
# Open in browser
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### Run Specific Test

```bash
pytest tests/contract/test_task_api.py::test_create_task -v
```

---

## Step 9: Interactive API Documentation

FastAPI automatically generates interactive API documentation.

### Swagger UI (Recommended)

Open in browser: [http://localhost:8000/docs](http://localhost:8000/docs)

**Features**:
- Interactive API explorer
- Try out endpoints directly
- View request/response schemas
- See example payloads

### ReDoc (Alternative)

Open in browser: [http://localhost:8000/redoc](http://localhost:8000/redoc)

**Features**:
- Clean, readable documentation
- Organized by tags
- Detailed schema descriptions

---

## Common Issues & Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'fastapi'"

**Solution**: Activate virtual environment and install dependencies
```bash
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### Issue: "Connection refused" when accessing database

**Solution**: Verify DATABASE_URL in `.env` file
```bash
# Check connection string format
echo $DATABASE_URL

# Test connection
python -c "from sqlmodel import create_engine; engine = create_engine('YOUR_DATABASE_URL'); print('OK')"
```

### Issue: "Address already in use" when starting server

**Solution**: Port 8000 is already in use
```bash
# Find process using port 8000
lsof -i :8000  # Linux/macOS
netstat -ano | findstr :8000  # Windows

# Kill the process or use a different port
uvicorn src.main:app --reload --port 8001
```

### Issue: Tests fail with "database locked" error

**Solution**: SQLite in-memory database issue (should not happen with proper fixtures)
```bash
# Ensure pytest fixtures are properly configured
# Check tests/conftest.py for session scope
```

### Issue: "422 Unprocessable Entity" when creating task

**Solution**: Invalid request body
```bash
# Ensure Content-Type header is set
curl -X POST http://localhost:8000/api/user123/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Test task"}'

# Check that title is not empty
# Check that title is <= 200 characters
# Check that description is <= 1000 characters
```

---

## Development Workflow

### 1. Make Code Changes

Edit files in `backend/src/`:
- `models/task.py` - Data models
- `routes/tasks.py` - API endpoints
- `services/task_service.py` - Business logic
- `schemas/task_schemas.py` - Request/response schemas

### 2. Run Tests

```bash
pytest
```

### 3. Check Code Quality

```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type check
mypy src/
```

### 4. Test Manually

```bash
# Start server with auto-reload
uvicorn src.main:app --reload

# Test endpoints with curl or Swagger UI
```

### 5. Commit Changes

```bash
git add .
git commit -m "[Task]: T-XXX - Description

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

---

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | - | Neon PostgreSQL connection string |
| `ENVIRONMENT` | No | `development` | Environment (development/staging/production) |
| `LOG_LEVEL` | No | `info` | Logging level (debug/info/warning/error) |

---

## Project Structure

```
backend/
├── src/
│   ├── models/
│   │   ├── __init__.py
│   │   └── task.py          # SQLModel Task entity
│   ├── routes/
│   │   ├── __init__.py
│   │   └── tasks.py         # FastAPI task endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   └── task_service.py  # Business logic
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── task_schemas.py  # Pydantic schemas
│   ├── middleware/
│   │   └── __init__.py
│   ├── db.py                # Database connection
│   ├── config.py            # Configuration
│   └── main.py              # FastAPI app entry point
├── tests/
│   ├── conftest.py          # Pytest fixtures
│   ├── contract/
│   │   └── test_task_api.py
│   ├── integration/
│   │   └── test_user_stories.py
│   └── unit/
│       └── test_task_service.py
├── .env                     # Environment variables (not in git)
├── .env.example             # Environment template
├── requirements.txt         # Python dependencies
└── README.md                # Backend documentation
```

---

## Next Steps

1. ✅ Backend API is running locally
2. ➡️ Run `/sp.tasks` to generate task breakdown
3. ➡️ Implement tasks using Claude Code
4. ➡️ Deploy backend to production (Vercel/Railway/Render)
5. ➡️ Integrate with frontend (Spec 2)
6. ➡️ Add JWT authentication (Spec 2)

---

## Additional Resources

- **FastAPI Documentation**: [fastapi.tiangolo.com](https://fastapi.tiangolo.com)
- **SQLModel Documentation**: [sqlmodel.tiangolo.com](https://sqlmodel.tiangolo.com)
- **Neon Documentation**: [neon.tech/docs](https://neon.tech/docs)
- **Pytest Documentation**: [docs.pytest.org](https://docs.pytest.org)
- **OpenAPI Specification**: See `specs/001-backend-task-api/contracts/openapi.yaml`

---

**Quickstart Status**: ✅ COMPLETE
**Ready for Development**: Yes
**Next Command**: `/sp.tasks` to generate task breakdown
