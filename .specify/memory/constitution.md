<!--
Sync Impact Report:
Version: 1.0.0 → 1.1.0 (Minor - Expanded Guidance)
Modified Principles:
  - Spec-Driven Development: Added explicit "no manual coding" enforcement
  - Security by Default: Expanded with deterministic behavior and environment parity requirements
  - API-First Design: Added explicit REST API correctness standards
Added Sections:
  - Deterministic Behavior principle (new explicit requirement)
  - Separation of Concerns principle (formalized existing practice)
  - Auditability principle (formalized existing practice)
Removed Sections: None
Templates Status:
  ✅ spec-template.md - Already aligned with user story prioritization
  ✅ tasks-template.md - Already aligned with independent testable tasks
  ✅ plan-template.md - Already aligned with constitution checks
Follow-up TODOs: None
Rationale: User provided refined principles that clarify and strengthen existing constitution without breaking compatibility. Emphasizes deterministic behavior, stricter spec-driven enforcement, and explicit separation of concerns.
-->

# Todo Full-Stack Web Application Constitution

## Core Principles

### I. Spec-Driven Development (NON-NEGOTIABLE)

**No code without specification. All implementation MUST be derived strictly from specs.**

Every feature MUST follow the SDD lifecycle:

- **Specify** → Define WHAT (requirements, user stories, acceptance criteria)
- **Plan** → Define HOW (architecture, components, interfaces)
- **Tasks** → Define BREAKDOWN (atomic, testable work units)
- **Implement** → Write code ONLY for approved tasks via Claude Code

**Rationale**: Prevents "vibe coding" and ensures alignment between requirements and implementation. All AI agents must verify task authorization before writing code. Eliminates manual coding drift and ensures all code is traceable to specifications.

**Enforcement**:
- **No manual coding**: All code MUST be generated via Claude Code using approved specs and plans
- Every code file MUST contain comments linking to Task ID and Spec sections
- No architectural changes without updating plan.md
- No feature additions without updating spec.md
- Constitution supersedes all other practices
- Specs must be independently reviewable before implementation begins

### II. Security-First Design (MANDATORY)

**Authentication, authorization, and user isolation MUST be enforced at all layers.**

- Better Auth with JWT tokens for session management
- All API endpoints require valid JWT (except auth endpoints)
- User data isolation: users only access their own resources
- Shared secret between frontend and backend for JWT verification
- No secrets in code: use environment variables
- **Stateless authentication**: JWT-based auth only, no server-side sessions
- **Data integrity**: All task operations MUST enforce ownership at database and API level

**Rationale**: Protects user data and prevents unauthorized access. Security is not optional. Stateless design enables horizontal scaling and simplifies deployment.

**Implementation**:
- Frontend: Attach JWT to every API request header
- Backend: Verify JWT and extract user_id on every protected endpoint
- Database: Filter all queries by authenticated user_id
- **Environment parity**: Frontend and backend MUST share JWT secret via environment variables (BETTER_AUTH_SECRET)
- **Error handling**: All authentication failures return clear, consistent HTTP status codes (401 Unauthorized, 403 Forbidden)

### III. Deterministic Behavior (MANDATORY)

**Same input MUST produce same output across all environments.**

- All operations must be reproducible
- No environment-specific behavior (except configuration)
- Consistent error handling and status codes
- Predictable state transitions
- No hidden side effects

**Rationale**: Ensures reliability, simplifies debugging, and enables confident deployment. Deterministic systems are easier to test, reason about, and maintain.

**Enforcement**:
- All API endpoints return consistent responses for identical inputs
- Database queries produce consistent results (proper ordering, filtering)
- Error messages are standardized and predictable
- No random behavior without explicit seeding
- Configuration via environment variables only

### IV. Separation of Concerns (MANDATORY)

**Backend, authentication, and frontend MUST be clearly isolated.**

- Backend and frontend are independent services
- Backend MUST NOT depend on frontend runtime
- Authentication verification occurs on every protected API request
- Clear boundaries between layers (models, services, routes, components)
- Each layer has single, well-defined responsibility

**Rationale**: Enables independent development, testing, and deployment. Reduces coupling and improves maintainability. Allows frontend and backend to evolve independently.

**Architectural Constraints**:
- Backend exposes RESTful API only
- Frontend consumes API as external service
- No shared runtime dependencies
- Authentication is stateless (JWT)
- Database access only through backend API

### V. Auditability (MANDATORY)

**Every decision MUST be traceable to specs, plans, or prompts.**

- All code references Task IDs and Spec sections
- Architectural decisions documented in ADRs
- Prompt History Records (PHRs) for all significant work
- Clear commit messages with task references
- Specification history maintained in version control

**Rationale**: Enables understanding of why decisions were made, facilitates onboarding, and supports debugging. Critical for hackathon evaluation and future maintenance.

**Implementation**:
- Code comments: `# [Task]: T-001 | [From]: specs/features/task-crud.md §2.1`
- PHRs created for all implementation work
- ADRs suggested for architectural decisions
- Git commits reference Task IDs
- Specs updated before implementation changes

### VI. Test-First Development (MANDATORY)

**TDD cycle strictly enforced** for all user-facing functionality:

1. Write tests that capture acceptance criteria
2. Verify tests FAIL (red)
3. Implement minimum code to pass (green)
4. Refactor while keeping tests green
5. Commit with test evidence

**Rationale**: Ensures code meets requirements and prevents regression. Tests serve as executable documentation.

**Scope**:
- Contract tests for all API endpoints
- Integration tests for user journeys
- Unit tests for complex business logic (optional unless specified)

### VII. Independent User Stories

**Every user story MUST be independently testable and deployable.**

- Prioritize stories (P1, P2, P3) by business value
- Each story delivers standalone value (viable MVP slice)
- Stories can be developed, tested, and deployed in isolation
- P1 stories are blocking; P2/P3 are incremental enhancements

**Rationale**: Enables iterative delivery, parallel development, and early validation. Reduces risk by delivering value incrementally.

### VIII. API-First Design

**All backend functionality exposed via RESTful APIs with strict contract adherence.**

- **REST API correctness**: Endpoints MUST match defined contracts exactly
- Clear endpoint contracts defined before implementation
- Request/response schemas documented in contracts/
- Consistent error handling and status codes
- JWT-based authentication for all protected endpoints

**Rationale**: Decouples frontend and backend, enables independent testing, and supports future API consumers.

**Standards**:
- GET /api/{user_id}/tasks - List tasks
- POST /api/{user_id}/tasks - Create task
- GET /api/{user_id}/tasks/{id} - Get task details
- PUT /api/{user_id}/tasks/{id} - Update task
- DELETE /api/{user_id}/tasks/{id} - Delete task
- PATCH /api/{user_id}/tasks/{id}/complete - Toggle completion

**Error Handling**:
- All failures return clear, consistent HTTP status codes
- 400 Bad Request - Invalid input
- 401 Unauthorized - Missing/invalid JWT
- 403 Forbidden - Valid JWT but insufficient permissions
- 404 Not Found - Resource doesn't exist
- 500 Internal Server Error - Server-side failures

### IX. Monorepo Organization

**Single repository with clear separation of concerns.**

```
/
├── .specify/           # Spec-Kit Plus configuration and templates
├── specs/              # Feature specifications
├── frontend/           # Next.js application
├── backend/            # FastAPI application
├── CLAUDE.md           # AI agent instructions
└── README.md           # Project documentation
```

**Rationale**: Simplifies cross-cutting changes, maintains single context for AI agents, and enables atomic commits across stack.

### X. Observability and Debugging

**All operations MUST be traceable and debuggable.**

- Structured logging for all API requests and errors
- Clear error messages (no stack traces to users)
- Request/response logging in development
- Database query logging for debugging

**Rationale**: Enables rapid debugging and issue resolution during development and hackathon evaluation.

## Technology Stack Constraints

### Frontend Requirements

- **Framework**: Next.js 16+ with App Router (MANDATORY)
- **Language**: TypeScript (MANDATORY)
- **Styling**: Tailwind CSS (MANDATORY)
- **Authentication**: Better Auth (MANDATORY)
- **Patterns**:
  - Server components by default
  - Client components only for interactivity
  - API calls through centralized client (/lib/api.ts)

### Backend Requirements

- **Framework**: Python FastAPI (MANDATORY)
- **ORM**: SQLModel (MANDATORY)
- **Database**: Neon Serverless PostgreSQL (MANDATORY)
- **Authentication**: JWT verification (MANDATORY)
- **Patterns**:
  - All routes under /api/
  - Pydantic models for request/response validation
  - HTTPException for error handling
  - Async/await for database operations

### Development Tools

- **Spec Management**: Spec-Kit Plus (MANDATORY)
- **AI Assistant**: Claude Code (MANDATORY)
- **Version Control**: Git with meaningful commit messages
- **Environment**: WSL 2 for Windows users

## Development Workflow

### Feature Development Cycle

1. **Specify**: Create spec.md with user stories and acceptance criteria
2. **Plan**: Generate plan.md with architecture and technical approach
3. **Tasks**: Break down into tasks.md with clear dependencies
4. **Implement**: Execute tasks in priority order (P1 → P2 → P3) via Claude Code
5. **Validate**: Test each user story independently
6. **Document**: Create PHR (Prompt History Record) for learning

### Workflow Constraints

- Follow Agentic Dev Stack strictly:
  1. Write spec
  2. Generate plan
  3. Break into tasks
  4. Implement via Claude Code
- No step may be skipped or merged
- Each spec must be independently reviewable
- Iterations must update specs before regenerating plans

### Code Review Requirements

- All code MUST reference Task ID in comments
- All API endpoints MUST have corresponding contract tests
- All user stories MUST have integration tests
- No hardcoded secrets or credentials
- No direct database access without user_id filtering

### Commit Standards

- Atomic commits per task or logical group
- Commit messages reference Task ID
- Include co-authorship: `Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>`
- Never commit .env files or credentials

## Quality Gates

### Before Implementation

- [ ] Spec.md approved with clear acceptance criteria
- [ ] Plan.md reviewed with architecture decisions
- [ ] Tasks.md created with independent, testable tasks
- [ ] Constitution compliance verified

### Before Deployment

- [ ] All P1 user stories tested independently
- [ ] API endpoints secured with JWT authentication
- [ ] Environment variables configured (no secrets in code)
- [ ] README.md updated with setup instructions
- [ ] Demo video prepared (max 90 seconds)

### Hackathon Submission

- [ ] Public GitHub repository with all source code
- [ ] /specs folder with all specification files
- [ ] CLAUDE.md with AI agent instructions
- [ ] Deployed frontend on Vercel
- [ ] Deployed backend with accessible API
- [ ] Demo video demonstrating all features

## Non-Functional Requirements

### Performance

- API response time: <500ms for CRUD operations
- Database queries: Indexed on user_id and task status
- Frontend: Optimistic UI updates for better UX

### Scalability

- Stateless backend (horizontal scaling ready)
- Connection pooling for database
- JWT-based auth (no server-side sessions)

### Maintainability

- Clear separation of concerns (models, services, routes)
- Consistent naming conventions
- Self-documenting code with minimal comments
- Comprehensive error handling

## Governance

### Amendment Process

1. Identify need for constitutional change
2. Document rationale and impact
3. Update constitution.md with version bump
4. Propagate changes to dependent templates
5. Create ADR for significant architectural decisions

### Version Semantics

- **MAJOR**: Backward incompatible changes (e.g., removing principles)
- **MINOR**: New principles or expanded guidance
- **PATCH**: Clarifications, typos, non-semantic refinements

### Compliance

- All PRs/reviews MUST verify constitution compliance
- Complexity MUST be justified in plan.md
- Use CLAUDE.md for runtime development guidance
- PHRs MUST be created for all significant work

### Conflict Resolution

When conflicts arise between artifacts, the hierarchy is:

1. **Constitution** (this file) - Highest authority
2. **Spec.md** - What to build
3. **Plan.md** - How to build
4. **Tasks.md** - Breakdown of work

**Version**: 1.1.0 | **Ratified**: 2026-02-07 | **Last Amended**: 2026-02-08
