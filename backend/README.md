# Backend Task API

FastAPI backend for secure, user-scoped task management with JWT authentication and persistent storage in Neon Serverless PostgreSQL.

## Quick Start

### Prerequisites

- Python 3.13 or higher
- pip (latest version)
- Neon PostgreSQL account (free tier available at [neon.tech](https://neon.tech))

### Setup

1. **Create virtual environment**:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```

2. **Install dependencies**:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Configure environment variables**:
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and configure the following required variables:

   ```env
   # Database Configuration
   DATABASE_URL=postgresql://user:password@host/database?sslmode=require

   # JWT Authentication Secret (CRITICAL - Must be shared with frontend)
   BETTER_AUTH_SECRET=your-secret-key-here-min-32-chars

   # Optional: Server Configuration
   HOST=0.0.0.0
   PORT=8000
   ```

   **Important Notes:**
   - `DATABASE_URL`: Get this from your Neon PostgreSQL dashboard
   - `BETTER_AUTH_SECRET`: Generate a secure random string (minimum 32 characters)
   - This secret MUST match the frontend's Better Auth configuration for JWT verification

4. **Generate JWT Secret** (if you don't have one):
   ```bash
   # Linux/macOS
   openssl rand -base64 32

   # Windows (PowerShell)
   [Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Minimum 0 -Maximum 256 }))

   # Python (any platform)
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

5. **Initialize database** (create tables):
   ```bash
   # The database tables will be created automatically on first run
   # Or you can run migrations manually:
   python -c "from src.db import init_db; init_db()"
   ```

6. **Run the server**:
   ```bash
   uvicorn src.main:app --reload
   ```

7. **Access API documentation**:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Authentication Setup

This backend uses JWT-based authentication with the following flow:

1. **User Signup** (`POST /api/auth/signup`):
   - User provides email, password, and optional name
   - Password is hashed using bcrypt (cost factor 12)
   - User record created in database with UUID
   - JWT token generated and set in httpOnly cookie
   - Returns user information (without password)

2. **User Signin** (`POST /api/auth/signin`):
   - User provides email and password
   - Password verified using bcrypt
   - JWT token generated and set in httpOnly cookie
   - Returns user information (without password)

3. **Protected Routes** (all `/api/{user_id}/tasks` endpoints):
   - Require valid JWT token in Authorization header or cookie
   - Token verified using `BETTER_AUTH_SECRET`
   - User ID extracted from token's `sub` claim
   - User data isolation enforced (users can only access their own tasks)

4. **Get Current User** (`GET /api/auth/me`):
   - Returns authenticated user's profile
   - Requires valid JWT token

5. **Signout** (`POST /api/auth/signout`):
   - Clears JWT cookie
   - Client-side token invalidation

**JWT Token Structure:**
```json
{
  "sub": "user-uuid",
  "email": "user@example.com",
  "iat": 1234567890,
  "exp": 1234654290
}
```

**Security Features:**
- Passwords hashed with bcrypt (never stored in plain text)
- JWT tokens signed with HS256 algorithm
- httpOnly cookies prevent XSS attacks
- Secure and SameSite=Strict flags for CSRF protection
- 24-hour token expiration
- User data isolation (403 Forbidden for unauthorized access)
- Generic error messages to prevent user enumeration

### Testing

Run all tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=src --cov-report=html
```

Run specific test suites:
```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# Contract tests only
pytest tests/contract/

# Authentication tests
pytest tests/unit/test_auth_service.py tests/unit/test_jwt_middleware.py
```

View coverage report:
```bash
# Generate HTML coverage report
pytest --cov=src --cov-report=html

# Open in browser (Linux/macOS)
open htmlcov/index.html

# Open in browser (Windows)
start htmlcov/index.html
```

### API Endpoints

#### Authentication Endpoints
- `POST /api/auth/signup` - Create new user account
- `POST /api/auth/signin` - Sign in to existing account
- `POST /api/auth/signout` - Sign out (clear JWT cookie)
- `GET /api/auth/me` - Get current user information (requires auth)

#### Task Endpoints (all require authentication)
- `POST /api/{user_id}/tasks` - Create task
- `GET /api/{user_id}/tasks` - List tasks
- `GET /api/{user_id}/tasks/{id}` - Get task
- `PUT /api/{user_id}/tasks/{id}` - Update task
- `DELETE /api/{user_id}/tasks/{id}` - Delete task
- `PATCH /api/{user_id}/tasks/{id}/complete` - Toggle completion

**Note:** All task endpoints require:
1. Valid JWT token (Authorization header or cookie)
2. URL `user_id` must match authenticated user's ID (403 Forbidden otherwise)

### Project Structure

```
backend/
├── src/
│   ├── models/          # SQLModel entities
│   │   ├── task.py      # Task model
│   │   └── user.py      # User model
│   ├── routes/          # FastAPI endpoints
│   │   ├── tasks.py     # Task CRUD endpoints
│   │   └── auth.py      # Authentication endpoints
│   ├── services/        # Business logic
│   │   ├── task_service.py    # Task operations
│   │   └── auth_service.py    # Auth operations
│   ├── schemas/         # Pydantic schemas
│   │   ├── task_schemas.py    # Task request/response
│   │   └── user_schemas.py    # User request/response
│   ├── middleware/      # Middleware components
│   │   └── jwt_auth.py  # JWT verification
│   ├── db.py           # Database connection
│   ├── config.py       # Configuration
│   └── main.py         # FastAPI app
├── tests/
│   ├── contract/       # API contract tests
│   ├── integration/    # Integration tests
│   └── unit/           # Unit tests
│       ├── test_auth_service.py      # AuthService tests
│       ├── test_jwt_middleware.py    # JWT middleware tests
│       └── test_task_service.py      # TaskService tests
├── requirements.txt    # Dependencies
├── .env               # Environment variables (not in git)
└── .env.example       # Environment template
```

## Troubleshooting

### Database Connection Issues

**Error:** `could not connect to server`
- Verify `DATABASE_URL` is correct in `.env`
- Check Neon dashboard for connection string
- Ensure `?sslmode=require` is appended to connection string

### Authentication Issues

**Error:** `Invalid authentication token`
- Verify `BETTER_AUTH_SECRET` is set in `.env`
- Ensure secret matches frontend configuration
- Check token hasn't expired (24-hour validity)

**Error:** `Access forbidden: You can only access your own resources`
- URL `user_id` doesn't match authenticated user's ID
- This is expected behavior for security (user data isolation)

### Import Errors

**Error:** `ModuleNotFoundError: No module named 'src'`
- Ensure you're running commands from the `backend/` directory
- Activate virtual environment: `source venv/bin/activate`

## Documentation

For detailed specifications:
- [Authentication Spec](../specs/002-auth-jwt/spec.md)
- [API Contracts](../specs/002-auth-jwt/contracts/auth-api.yaml)
- [Task API Spec](../specs/001-backend-task-api/spec.md)
- [Quickstart Guide](../specs/001-backend-task-api/quickstart.md)

## Development

### Adding New Endpoints

1. Define Pydantic schemas in `src/schemas/`
2. Create route handler in `src/routes/`
3. Implement business logic in `src/services/`
4. Add tests in `tests/`
5. Update API documentation

### Database Migrations

Currently using SQLModel's automatic table creation. For production:
1. Use Alembic for migrations
2. Version control schema changes
3. Test migrations on staging before production

### Logging

Structured logging is configured for all endpoints:
- **INFO**: Successful operations (signup, signin, task operations)
- **WARNING**: Authentication failures, authorization violations, not found errors
- **ERROR**: Unexpected errors with stack traces
- **DEBUG**: Detailed debugging information (JWT verification, etc.)

Logs include:
- User IDs (for audit trail)
- Operation types (create, update, delete, etc.)
- Task IDs (for specific operations)
- Error details (without sensitive data)

**Note:** Passwords and JWT tokens are never logged.
"# Todo-app" 
