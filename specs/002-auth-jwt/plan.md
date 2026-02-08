# Implementation Plan: Authentication & User Context

**Branch**: `002-auth-jwt` | **Date**: 2026-02-08 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-auth-jwt/spec.md`

## Summary

Implement secure authentication and user context management for the todo application using Better Auth on the frontend and JWT verification on the backend. Users will be able to sign up, sign in, and access their personal task data with enforced user isolation. All API requests will be authenticated using JWT tokens, and the backend will verify token signatures using a shared secret.

## Technical Context

**Language/Version**:
- Frontend: TypeScript with Next.js 16+
- Backend: Python 3.13+

**Primary Dependencies**:
- Frontend: Better Auth, Next.js App Router, Tailwind CSS
- Backend: FastAPI, SQLModel, PyJWT, python-dotenv

**Storage**:
- Neon Serverless PostgreSQL (existing)
- User accounts table (new)
- Tasks table (existing, add user_id foreign key if not present)

**Testing**:
- Frontend: Jest/Vitest for component tests
- Backend: pytest for API contract tests and integration tests

**Target Platform**:
- Frontend: Vercel (serverless)
- Backend: Vercel/Railway/Render (serverless/container)

**Project Type**: Web application (frontend + backend)

**Performance Goals**:
- Sign-in: <2 seconds under normal load
- Token verification: <50ms latency per request
- Account creation: <1 minute for valid credentials

**Constraints**:
- Stateless authentication (no server-side sessions)
- JWT tokens valid for 24 hours
- Shared secret between frontend and backend (BETTER_AUTH_SECRET)
- All protected endpoints require valid JWT
- User data isolation enforced at database and API level

**Scale/Scope**:
- Multi-user application (10-1000 users expected)
- 3 user stories (P1: auth, P2: isolation, P3: sessions)
- 13 functional requirements
- 6 API endpoints to secure (existing task CRUD)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ Spec-Driven Development
- Specification complete with 3 prioritized user stories
- All functional requirements defined (FR-001 to FR-013)
- Success criteria measurable and technology-agnostic
- Ready to proceed with planning

### ✅ Security-First Design
- JWT-based authentication specified
- User data isolation required (FR-008, FR-013)
- Shared secret for token signing (FR-012)
- No secrets in code (environment variables)
- Stateless authentication enforced

### ✅ Deterministic Behavior
- Same credentials produce same authentication result
- Token verification is deterministic (signature check)
- Consistent error codes specified (401, 403)
- No random behavior in auth flow

### ✅ Separation of Concerns
- Frontend handles auth UI and token storage
- Backend handles token verification independently
- No shared runtime dependencies
- Clear API boundary between services

### ✅ Auditability
- All requirements traceable to spec
- ADR needed for JWT payload structure decision
- PHR will document implementation work

### ✅ Test-First Development
- Contract tests required for auth endpoints
- Integration tests for user journeys
- TDD cycle will be followed

### ✅ Independent User Stories
- P1: Basic auth (signup/signin) - independently testable
- P2: User isolation - independently testable
- P3: Session persistence - independently testable

### ✅ API-First Design
- Auth endpoints will follow REST conventions
- POST /api/auth/signup, POST /api/auth/signin
- Existing task endpoints secured with JWT middleware
- Consistent error handling

**Gate Status**: ✅ PASS - All constitution principles satisfied

## Project Structure

### Documentation (this feature)

```text
specs/002-auth-jwt/
├── spec.md              # Feature specification (complete)
├── plan.md              # This file
├── research.md          # Phase 0 output (to be created)
├── data-model.md        # Phase 1 output (to be created)
├── quickstart.md        # Phase 1 output (to be created)
├── contracts/           # Phase 1 output (to be created)
│   ├── auth-api.yaml    # Authentication endpoints
│   └── secured-tasks-api.yaml  # Updated task endpoints with auth
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── task.py          # Existing task model
│   │   └── user.py          # NEW: User account model
│   ├── services/
│   │   ├── task_service.py  # Existing task service
│   │   └── auth_service.py  # NEW: Authentication service
│   ├── middleware/
│   │   └── jwt_auth.py      # NEW: JWT verification middleware
│   ├── routes/
│   │   ├── tasks.py         # MODIFY: Add JWT dependency
│   │   └── auth.py          # NEW: Auth endpoints (signup, signin)
│   ├── config.py            # MODIFY: Add JWT secret config
│   ├── db.py                # Existing database connection
│   └── main.py              # MODIFY: Register auth routes and middleware
├── tests/
│   ├── contract/
│   │   ├── test_task_api.py      # MODIFY: Add auth headers
│   │   └── test_auth_api.py      # NEW: Auth endpoint tests
│   ├── integration/
│   │   └── test_user_isolation.py # NEW: User isolation tests
│   └── unit/
│       └── test_jwt_middleware.py # NEW: JWT verification tests
├── .env                     # MODIFY: Add BETTER_AUTH_SECRET
└── requirements.txt         # MODIFY: Add PyJWT

frontend/
├── src/
│   ├── app/
│   │   ├── (auth)/
│   │   │   ├── signin/
│   │   │   │   └── page.tsx     # NEW: Sign-in page
│   │   │   └── signup/
│   │   │       └── page.tsx     # NEW: Sign-up page
│   │   ├── dashboard/
│   │   │   └── page.tsx         # MODIFY: Add auth check
│   │   └── layout.tsx           # MODIFY: Add auth provider
│   ├── components/
│   │   └── auth/
│   │       ├── SignInForm.tsx   # NEW: Sign-in form component
│   │       └── SignUpForm.tsx   # NEW: Sign-up form component
│   ├── lib/
│   │   ├── api.ts               # MODIFY: Add JWT token attachment
│   │   └── auth.ts              # NEW: Better Auth configuration
│   └── middleware.ts            # NEW: Route protection middleware
├── .env.local                   # MODIFY: Add BETTER_AUTH_SECRET
└── package.json                 # MODIFY: Add better-auth dependency
```

**Structure Decision**: Web application structure (Option 2) selected. Frontend and backend are independent services with clear API boundary. Authentication is handled by Better Auth on frontend with JWT verification on backend. Existing task API will be secured with JWT middleware.

## Complexity Tracking

No constitution violations. All complexity is justified by requirements:
- JWT authentication is industry standard for stateless auth
- Better Auth simplifies frontend auth implementation
- Middleware pattern is standard for cross-cutting concerns
- User isolation is security requirement, not premature optimization

---

## Post-Design Constitution Re-Check

*Re-evaluated after Phase 1 (Design & Contracts) completion*

### ✅ Spec-Driven Development
- All design artifacts reference spec requirements
- API contracts match functional requirements (FR-001 to FR-013)
- Data model entities map to spec entities
- No implementation without specification

### ✅ Security-First Design
- JWT verification enforced at middleware layer
- User isolation enforced at route, service, and database layers
- Password hashing with bcrypt (industry standard)
- httpOnly cookies prevent XSS attacks
- Shared secret managed via environment variables

### ✅ Deterministic Behavior
- JWT verification is deterministic (signature check)
- Password hashing produces consistent results
- API responses follow OpenAPI contracts
- Error codes are standardized (401, 403, 404)

### ✅ Separation of Concerns
- Frontend: Better Auth handles UI and token issuance
- Backend: JWT middleware handles verification independently
- Clear API boundary defined in contracts/
- No shared runtime dependencies

### ✅ Auditability
- All design decisions documented in research.md
- API contracts provide clear interface definitions
- Data model documents all entities and relationships
- Quickstart provides implementation traceability

### ✅ Test-First Development
- Contract tests defined in OpenAPI specs
- Integration test scenarios defined in data-model.md
- Quickstart includes comprehensive testing checklist
- TDD cycle ready for implementation phase

### ✅ Independent User Stories
- P1 (auth) can be implemented and tested independently
- P2 (isolation) builds on P1 but is independently testable
- P3 (sessions) builds on P1 but is independently testable
- Each story delivers standalone value

### ✅ API-First Design
- OpenAPI contracts define all endpoints before implementation
- Request/response schemas fully specified
- Error responses standardized
- Authentication requirements explicit

**Final Gate Status**: ✅ PASS - All constitution principles satisfied after design phase

**Ready for**: `/sp.tasks` command to generate task breakdown
