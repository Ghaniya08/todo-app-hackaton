# Implementation Plan: Backend Task API & Data Layer

**Branch**: `001-backend-task-api` | **Date**: 2026-02-08 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-backend-task-api/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a production-ready FastAPI backend that provides secure, user-scoped task management with persistent storage in Neon Serverless PostgreSQL. The backend exposes 6 RESTful API endpoints for complete CRUD operations on tasks, with strict enforcement of user data isolation at both the API and database layers. All endpoints accept user_id as a path parameter and filter operations to ensure users can only access their own tasks. The system is designed to be stateless and JWT-ready, with authentication middleware to be added in a future specification.

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**: FastAPI (web framework), SQLModel (ORM), psycopg2-binary (PostgreSQL driver), pydantic (validation)
**Storage**: Neon Serverless PostgreSQL (connection via DATABASE_URL environment variable)
**Testing**: pytest (unit/integration), httpx (async HTTP client for API testing)
**Target Platform**: Linux server (containerizable, cloud-deployable)
**Project Type**: Web application (backend API only)
**Performance Goals**: <500ms p95 latency for all CRUD operations, <500ms for listing 100 tasks
**Constraints**: User data isolation (100% enforcement), stateless architecture (JWT-ready), no server-side sessions, deterministic responses
**Scale/Scope**: Multi-user system, 6 API endpoints, single Task entity, designed for horizontal scaling

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ I. Spec-Driven Development (NON-NEGOTIABLE)
- **Status**: PASS
- **Evidence**: Complete spec.md exists with user stories, acceptance criteria, and functional requirements
- **Enforcement**: All code will reference Task IDs and Spec sections; no manual coding permitted

### ✅ II. Security-First Design (MANDATORY)
- **Status**: PASS
- **Evidence**: User data isolation enforced at API and database level (FR-009, FR-010)
- **Implementation**: All queries filtered by user_id; ownership validation on all operations
- **Note**: JWT verification deferred to Spec 2 as documented in assumptions

### ✅ III. Deterministic Behavior (MANDATORY)
- **Status**: PASS
- **Evidence**: REST API with consistent status codes (FR-013 through FR-018), predictable responses
- **Implementation**: Same input produces same output; no random behavior; standardized error handling

### ✅ IV. Separation of Concerns (MANDATORY)
- **Status**: PASS
- **Evidence**: Backend-only specification; no frontend dependencies; clear layer separation
- **Architecture**: Models → Services → Routes pattern; database access only through ORM

### ✅ V. Auditability (MANDATORY)
- **Status**: PASS
- **Evidence**: All code will include Task ID and Spec section references in comments
- **Implementation**: PHR will be created; ADR suggested if architectural decisions made

### ✅ VI. Test-First Development (MANDATORY)
- **Status**: PASS
- **Evidence**: Contract tests required for all 6 endpoints; integration tests for user stories
- **Implementation**: TDD cycle enforced (red → green → refactor)

### ✅ VII. Independent User Stories
- **Status**: PASS
- **Evidence**: P1 (Create/View), P2 (Update/Delete), P3 (Complete) - each independently testable
- **Implementation**: Stories can be developed and deployed in isolation

### ✅ VIII. API-First Design
- **Status**: PASS
- **Evidence**: 6 REST endpoints defined with exact contracts (FR-003 through FR-008)
- **Implementation**: Request/response schemas documented; consistent error handling

### ✅ IX. Monorepo Organization
- **Status**: PASS
- **Evidence**: Backend code in /backend directory; specs in /specs directory
- **Implementation**: Clear separation maintained

### ✅ X. Observability and Debugging
- **Status**: PASS
- **Evidence**: Structured logging planned; clear error messages; no stack traces to users
- **Implementation**: Request/response logging in development; database query logging

**GATE RESULT**: ✅ ALL CHECKS PASSED - Proceed to Phase 0

## Project Structure

### Documentation (this feature)

```text
specs/001-backend-task-api/
├── spec.md              # Feature specification (COMPLETE)
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   ├── openapi.yaml     # OpenAPI 3.0 specification
│   └── schemas.json     # Request/response schemas
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
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
│   │   └── task_service.py  # Business logic layer
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── task_schemas.py  # Pydantic request/response models
│   ├── middleware/
│   │   ├── __init__.py
│   │   └── (future JWT verification)
│   ├── db.py                # Database connection and session management
│   ├── config.py            # Environment-based configuration
│   └── main.py              # FastAPI app entry point, CORS, middleware
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Pytest fixtures (test database, client)
│   ├── contract/
│   │   ├── __init__.py
│   │   └── test_task_api.py # API contract tests (all 6 endpoints)
│   ├── integration/
│   │   ├── __init__.py
│   │   └── test_user_stories.py # User story integration tests
│   └── unit/
│       ├── __init__.py
│       └── test_task_service.py # Business logic unit tests
├── .env.example             # Environment variable template
├── requirements.txt         # Python dependencies
└── README.md                # Backend setup instructions
```

**Structure Decision**: Web application structure selected (Option 2 from template). Backend is isolated in /backend directory with clear separation between models (data), services (business logic), routes (API), and schemas (validation). This structure supports the Separation of Concerns principle and enables independent testing of each layer. Tests are organized by type (contract, integration, unit) to support TDD workflow.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

*No violations detected. All constitution checks passed.*

## Phase 0: Research & Unknowns

### Research Tasks

1. **FastAPI Best Practices for Neon Serverless PostgreSQL**
   - Research: Connection pooling strategies for serverless databases
   - Research: Async database operations with SQLModel
   - Research: Environment-based configuration patterns
   - Output: Recommended connection settings and session management approach

2. **SQLModel Schema Design**
   - Research: Best practices for timestamp fields (created_at, updated_at)
   - Research: Auto-increment primary key configuration
   - Research: Foreign key relationships (user_id as string)
   - Output: Optimal Task model definition with proper indexes

3. **REST API Error Handling Patterns**
   - Research: FastAPI HTTPException best practices
   - Research: Consistent JSON error response format
   - Research: Status code conventions for ownership violations
   - Output: Standardized error handling middleware

4. **Testing Strategy for FastAPI**
   - Research: pytest-asyncio for async endpoint testing
   - Research: Test database setup and teardown patterns
   - Research: Fixture design for test data isolation
   - Output: Testing framework configuration and patterns

### Unknowns to Resolve

- **Database Connection Pooling**: How to configure connection pooling for Neon Serverless PostgreSQL to optimize performance while avoiding connection exhaustion?
- **Timestamp Management**: Should timestamps be managed by SQLModel (Python) or PostgreSQL (database triggers)? Which approach is more reliable?
- **User ID Validation**: Should we validate user_id format (e.g., UUID, alphanumeric) or accept any string? What are the security implications?
- **Error Response Format**: What JSON structure should error responses use? Should we follow RFC 7807 (Problem Details) or a custom format?
- **Test Database Strategy**: Should tests use an in-memory SQLite database or a separate Neon test database? What are the tradeoffs?

**Output**: `research.md` with all unknowns resolved and decisions documented

## Phase 1: Design & Contracts

### Data Model Design

**Entity**: Task

**Fields**:
- `id`: Integer (primary key, auto-increment)
- `user_id`: String (indexed, not null) - foreign key to user (managed externally)
- `title`: String (max 200 chars, not null)
- `description`: String (max 1000 chars, nullable)
- `completed`: Boolean (default False, not null)
- `created_at`: DateTime (UTC, auto-set on creation)
- `updated_at`: DateTime (UTC, auto-update on modification)

**Indexes**:
- Primary: `id`
- Foreign: `user_id` (for filtering by user)
- Composite: `(user_id, completed)` (for future filtering by status)

**Validation Rules**:
- Title: Required, 1-200 characters
- Description: Optional, max 1000 characters
- User ID: Required, string format
- Completed: Boolean only (true/false)

**State Transitions**:
- New task: `completed = False`
- Toggle completion: `completed = !completed`
- Update: `updated_at` refreshed automatically

**Output**: `data-model.md` with complete entity definition

### API Contracts

**Base Path**: `/api/{user_id}/tasks`

**Endpoints**:

1. **POST /api/{user_id}/tasks** - Create Task
   - Request: `{ "title": string, "description": string? }`
   - Response 201: `{ "id": int, "user_id": string, "title": string, "description": string?, "completed": bool, "created_at": datetime, "updated_at": datetime }`
   - Response 400: `{ "error": string, "detail": string }`

2. **GET /api/{user_id}/tasks** - List Tasks
   - Request: None
   - Response 200: `[{ task object }, ...]` (array of tasks, newest first)

3. **GET /api/{user_id}/tasks/{id}** - Get Task
   - Request: None
   - Response 200: `{ task object }`
   - Response 404: `{ "error": "Task not found" }`

4. **PUT /api/{user_id}/tasks/{id}** - Update Task
   - Request: `{ "title": string, "description": string? }`
   - Response 200: `{ task object }`
   - Response 404: `{ "error": "Task not found" }`
   - Response 400: `{ "error": string, "detail": string }`

5. **DELETE /api/{user_id}/tasks/{id}** - Delete Task
   - Request: None
   - Response 204: No content
   - Response 404: `{ "error": "Task not found" }`

6. **PATCH /api/{user_id}/tasks/{id}/complete** - Toggle Completion
   - Request: None
   - Response 200: `{ task object }` (with toggled completed status)
   - Response 404: `{ "error": "Task not found" }`

**Output**: `contracts/openapi.yaml` and `contracts/schemas.json`

### Quickstart Guide

**Output**: `quickstart.md` with:
- Environment setup (Python 3.13+, virtual environment)
- Database setup (Neon connection string)
- Dependency installation (`pip install -r requirements.txt`)
- Running the server (`uvicorn src.main:app --reload`)
- Testing endpoints (curl examples)
- Running tests (`pytest`)

### Agent Context Update

**Action**: Run `.specify/scripts/powershell/update-agent-context.ps1 -AgentType claude`

**Technologies to Add**:
- FastAPI (web framework)
- SQLModel (ORM)
- Neon Serverless PostgreSQL (database)
- pytest (testing)
- httpx (async HTTP client)
- pydantic (validation)

**Output**: Updated agent context file with new technologies

## Phase 2: Task Breakdown

**Note**: This phase is executed by the `/sp.tasks` command, NOT by `/sp.plan`.

The `/sp.tasks` command will generate `tasks.md` with atomic, testable work units based on this plan and the feature specification.

## Implementation Strategy

### Development Sequence

**Phase 1: Foundation (P1 - Create/View Tasks)**
1. Set up FastAPI project structure
2. Configure database connection (Neon PostgreSQL)
3. Define Task SQLModel entity
4. Implement POST /api/{user_id}/tasks (create)
5. Implement GET /api/{user_id}/tasks (list)
6. Implement GET /api/{user_id}/tasks/{id} (get)
7. Write contract tests for P1 endpoints
8. Write integration tests for User Story 1

**Phase 2: Maintenance (P2 - Update/Delete Tasks)**
1. Implement PUT /api/{user_id}/tasks/{id} (update)
2. Implement DELETE /api/{user_id}/tasks/{id} (delete)
3. Write contract tests for P2 endpoints
4. Write integration tests for User Story 2

**Phase 3: Completion (P3 - Mark Complete)**
1. Implement PATCH /api/{user_id}/tasks/{id}/complete (toggle)
2. Write contract tests for P3 endpoint
3. Write integration tests for User Story 3

### Testing Strategy

**Contract Tests** (tests/contract/test_task_api.py):
- Test each endpoint with valid inputs
- Test each endpoint with invalid inputs
- Verify exact HTTP status codes
- Verify response schema compliance
- Test ownership enforcement (cross-user access)

**Integration Tests** (tests/integration/test_user_stories.py):
- Test complete user journeys (P1, P2, P3)
- Test edge cases from spec
- Test data persistence across requests
- Test user data isolation

**Unit Tests** (tests/unit/test_task_service.py):
- Test business logic in isolation
- Test validation rules
- Test error handling

### Deployment Readiness

**Environment Variables**:
- `DATABASE_URL`: Neon PostgreSQL connection string
- `ENVIRONMENT`: dev/staging/production
- `LOG_LEVEL`: debug/info/warning/error

**Health Check**:
- Endpoint: GET /health
- Response: `{ "status": "healthy", "database": "connected" }`

**CORS Configuration**:
- Allow origins: Frontend URL (to be configured)
- Allow methods: GET, POST, PUT, PATCH, DELETE
- Allow headers: Content-Type, Authorization (for future JWT)

## Risk Analysis

### Technical Risks

1. **Database Connection Pooling**
   - Risk: Connection exhaustion with Neon Serverless PostgreSQL
   - Mitigation: Research optimal pooling settings in Phase 0; implement connection limits
   - Blast Radius: All API requests fail if connections exhausted
   - Kill Switch: Implement connection timeout and retry logic

2. **User Data Isolation**
   - Risk: Query logic error could leak cross-user data
   - Mitigation: Comprehensive contract tests for ownership enforcement; code review
   - Blast Radius: Privacy violation, hackathon disqualification
   - Kill Switch: All queries MUST filter by user_id; no exceptions

3. **Performance Degradation**
   - Risk: Slow queries as task count grows
   - Mitigation: Database indexes on user_id and completed fields
   - Blast Radius: Poor user experience, failed performance requirements
   - Kill Switch: Query optimization; pagination (future enhancement)

### Operational Risks

1. **Environment Configuration**
   - Risk: Missing DATABASE_URL causes startup failure
   - Mitigation: Validate environment variables on startup; clear error messages
   - Blast Radius: Backend unavailable
   - Kill Switch: Fail fast with descriptive error

2. **Database Migration**
   - Risk: Schema changes could break existing data
   - Mitigation: Use SQLModel's create_all() for initial setup; plan migrations carefully
   - Blast Radius: Data loss or corruption
   - Kill Switch: Database backups; rollback capability

## Architectural Decisions

### Decision 1: SQLModel for ORM

**Context**: Need to interact with PostgreSQL database from Python backend.

**Options Considered**:
1. SQLModel (SQLAlchemy + Pydantic)
2. Raw SQLAlchemy
3. Django ORM
4. Raw SQL with psycopg2

**Decision**: Use SQLModel

**Rationale**:
- Combines SQLAlchemy (mature ORM) with Pydantic (validation)
- Type hints for better IDE support and error detection
- Seamless integration with FastAPI (both use Pydantic)
- Reduces boilerplate (single model for DB and API)
- Constitution mandates SQLModel

**Tradeoffs**:
- Less mature than pure SQLAlchemy
- Smaller community and fewer resources
- Acceptable: Benefits outweigh risks for this project

**ADR Suggestion**: 📋 Architectural decision detected: SQLModel as ORM for FastAPI backend. Document reasoning and tradeoffs? Run `/sp.adr sqlmodel-orm-choice`

### Decision 2: User ID as String in Path Parameter

**Context**: Need to identify which user's tasks to operate on.

**Options Considered**:
1. User ID in path parameter (e.g., /api/{user_id}/tasks)
2. User ID extracted from JWT token (Authorization header)
3. User ID in query parameter (e.g., /api/tasks?user_id=123)

**Decision**: User ID in path parameter (Option 1)

**Rationale**:
- Spec explicitly requires this pattern (FR-003 through FR-008)
- RESTful design: resource ownership clear in URL
- Prepares for JWT integration (Spec 2 will validate path user_id matches token)
- Simplifies testing without authentication

**Tradeoffs**:
- Temporarily accepts any user_id (no validation)
- Requires JWT middleware in Spec 2 to validate ownership
- Acceptable: Spec 2 will add security layer

**ADR Suggestion**: Not needed (follows REST conventions and spec requirements)

### Decision 3: No Pagination for Task List

**Context**: GET /api/{user_id}/tasks returns all tasks for a user.

**Options Considered**:
1. Return all tasks (no pagination)
2. Implement cursor-based pagination
3. Implement offset-based pagination

**Decision**: Return all tasks (Option 1)

**Rationale**:
- Spec assumption: "No pagination is required for the task list endpoint"
- Performance goal: <500ms for 100 tasks (achievable without pagination)
- Simplifies initial implementation
- Can be added in future phases if needed

**Tradeoffs**:
- May not scale to thousands of tasks per user
- Acceptable: Phase II scope is limited; Phase V can add pagination

**ADR Suggestion**: Not needed (follows spec assumptions)

## Success Metrics

### Definition of Done

- [ ] All 6 API endpoints implemented and functional
- [ ] All contract tests passing (100% endpoint coverage)
- [ ] All integration tests passing (P1, P2, P3 user stories)
- [ ] User data isolation verified (cross-user access tests)
- [ ] Data persistence verified (tasks survive server restart)
- [ ] Performance requirements met (<500ms for CRUD operations)
- [ ] Error handling complete (all 4xx/5xx scenarios)
- [ ] Code references Task IDs and Spec sections
- [ ] Backend deployable independently (no frontend dependency)
- [ ] README.md with setup instructions
- [ ] PHR created for implementation work

### Validation Checklist

**Functional Validation**:
- [ ] Can create task with valid data → 201 response
- [ ] Can list all tasks for user → 200 response with array
- [ ] Can get specific task → 200 response with task object
- [ ] Can update task → 200 response with updated task
- [ ] Can delete task → 204 response
- [ ] Can toggle task completion → 200 response with toggled status

**Security Validation**:
- [ ] User A cannot access User B's tasks → 404 response
- [ ] All queries filtered by user_id
- [ ] No cross-user data leakage

**Error Handling Validation**:
- [ ] Empty title → 400 Bad Request
- [ ] Title >200 chars → 400 Bad Request
- [ ] Description >1000 chars → 400 Bad Request
- [ ] Non-existent task → 404 Not Found
- [ ] Database error → 500 Internal Server Error

**Performance Validation**:
- [ ] Create task <500ms
- [ ] List 100 tasks <500ms
- [ ] Get task <500ms
- [ ] Update task <500ms
- [ ] Delete task <500ms
- [ ] Toggle completion <500ms

## Next Steps

1. **Execute Phase 0**: Run research tasks and create `research.md`
2. **Execute Phase 1**: Create `data-model.md`, `contracts/`, and `quickstart.md`
3. **Update Agent Context**: Run update script to add technologies
4. **Re-evaluate Constitution**: Verify all checks still pass after design
5. **Generate Tasks**: Run `/sp.tasks` command to create `tasks.md`
6. **Implement**: Execute tasks via Claude Code with specialized agents
7. **Test**: Run contract and integration tests
8. **Document**: Create PHR for implementation work
9. **Deploy**: Prepare backend for independent deployment

---

**Plan Status**: ✅ COMPLETE - Ready for Phase 0 Research
**Constitution Compliance**: ✅ ALL CHECKS PASSED
**Next Command**: Begin Phase 0 research or proceed to `/sp.tasks` if research is complete
