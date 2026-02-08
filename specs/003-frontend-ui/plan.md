# Implementation Plan: Frontend UI & Integration

**Branch**: `003-frontend-ui` | **Date**: 2026-02-08 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-frontend-ui/spec.md`

## Summary

Implement a responsive, authenticated task management UI using Next.js 16+ App Router that integrates with the existing backend API. Users will be able to sign up, sign in, and manage their personal tasks through a clean web interface. The frontend will handle authentication via Better Auth, attach JWT tokens to all API requests, and provide comprehensive loading and error states for a professional user experience.

## Technical Context

**Language/Version**: TypeScript with Next.js 16+ (App Router)
**Primary Dependencies**: Better Auth, React 18+, Tailwind CSS, Next.js App Router
**Storage**: Browser cookies (httpOnly for JWT tokens), React state management
**Testing**: Jest/Vitest for component tests, Playwright/Cypress for E2E tests
**Target Platform**: Modern web browsers (Chrome, Firefox, Safari, Edge - last 2 versions)
**Project Type**: Web application (frontend only - backend already exists)
**Performance Goals**: Initial load <3s, task operations <500ms feedback, page transitions <200ms
**Constraints**:
- Must integrate with existing backend API (localhost:8000 in dev)
- JWT tokens in httpOnly cookies only (no localStorage)
- Responsive design (320px+ mobile to desktop)
- No manual coding - all via Claude Code
**Scale/Scope**:
- 3 user stories (P1: auth, P2: task management, P3: session persistence)
- 5 pages (signup, signin, dashboard, task edit, 404)
- 18 functional requirements
- Integration with 10 backend API endpoints

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ Spec-Driven Development
- Specification complete with 3 prioritized user stories
- All functional requirements defined (FR-001 to FR-018)
- Success criteria measurable and technology-agnostic
- Ready to proceed with planning
- No manual coding - all implementation via Claude Code

### ✅ Security-First Design
- JWT-based authentication via Better Auth
- Tokens stored in httpOnly cookies (XSS protection)
- All API requests include authentication token
- Protected routes redirect unauthenticated users
- User data isolation enforced on frontend (display only user's tasks)
- No secrets in code (environment variables for API URL and auth secret)

### ✅ Deterministic Behavior
- Same user actions produce same API calls
- Consistent error handling and status codes
- Predictable UI state transitions
- No random behavior in UI
- Environment-specific config via .env only

### ✅ Separation of Concerns
- Frontend and backend are independent services
- Frontend consumes backend as external REST API
- Clear separation: pages, components, services, utilities
- Authentication handled by Better Auth library
- API client isolated from UI components

### ✅ Auditability
- All requirements traceable to spec
- ADR needed for Better Auth vs NextAuth decision
- PHR will document implementation work
- Component structure follows Next.js conventions

### ✅ Test-First Development
- Component tests for UI elements
- Integration tests for user journeys
- E2E tests for critical flows
- TDD cycle will be followed where applicable

### ✅ Independent User Stories
- P1: Authentication UI - independently testable
- P2: Task management UI - independently testable
- P3: Session persistence - independently testable

### ✅ API-First Design
- Backend API already defined and functional
- Frontend consumes existing REST endpoints
- API client follows REST conventions
- Consistent error handling

**Gate Status**: ✅ PASS - All constitution principles satisfied

## Project Structure

### Documentation (this feature)

```text
specs/003-frontend-ui/
├── spec.md              # Feature specification (complete)
├── plan.md              # This file
├── research.md          # Phase 0 output (to be created)
├── data-model.md        # Phase 1 output (to be created)
├── quickstart.md        # Phase 1 output (to be created)
├── contracts/           # Phase 1 output (to be created)
│   └── api-client.ts    # TypeScript API client interface
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
frontend/
├── src/
│   ├── app/
│   │   ├── (auth)/
│   │   │   ├── signin/
│   │   │   │   └── page.tsx     # Sign-in page
│   │   │   └── signup/
│   │   │       └── page.tsx     # Sign-up page
│   │   ├── dashboard/
│   │   │   └── page.tsx         # Protected dashboard with task list
│   │   ├── layout.tsx           # Root layout with auth provider
│   │   ├── page.tsx             # Landing page (redirects to signin/dashboard)
│   │   └── globals.css          # Global styles (Tailwind)
│   ├── components/
│   │   ├── auth/
│   │   │   ├── SignInForm.tsx   # Sign-in form component
│   │   │   └── SignUpForm.tsx   # Sign-up form component
│   │   ├── tasks/
│   │   │   ├── TaskList.tsx     # Task list display
│   │   │   ├── TaskItem.tsx     # Individual task item
│   │   │   ├── TaskForm.tsx     # Create/edit task form
│   │   │   └── EmptyState.tsx   # Empty state when no tasks
│   │   └── ui/
│   │       ├── Button.tsx       # Reusable button component
│   │       ├── Input.tsx        # Reusable input component
│   │       ├── Spinner.tsx      # Loading spinner
│   │       └── ErrorMessage.tsx # Error message display
│   ├── lib/
│   │   ├── api.ts               # API client for backend requests
│   │   ├── auth.ts              # Better Auth configuration
│   │   └── utils.ts             # Utility functions
│   ├── types/
│   │   ├── task.ts              # Task type definitions
│   │   └── user.ts              # User type definitions
│   └── middleware.ts            # Route protection middleware
├── public/
│   └── favicon.ico              # Favicon
├── tests/
│   ├── components/              # Component tests
│   ├── integration/             # Integration tests
│   └── e2e/                     # End-to-end tests
├── .env.local                   # Environment variables (not committed)
├── .env.example                 # Environment variable template
├── next.config.js               # Next.js configuration
├── tailwind.config.js           # Tailwind CSS configuration
├── tsconfig.json                # TypeScript configuration
├── package.json                 # Dependencies
└── README.md                    # Frontend documentation
```

**Structure Decision**: Web application structure (frontend only). Backend already exists from Phase II (002-auth-jwt). Frontend is a separate Next.js application that consumes the backend REST API. Uses Next.js 16+ App Router with TypeScript, Better Auth for authentication, and Tailwind CSS for styling.

## Complexity Tracking

No constitution violations. All complexity is justified by requirements:
- Next.js App Router is the modern standard for React applications
- Better Auth simplifies authentication with JWT support
- TypeScript provides type safety and better developer experience
- Tailwind CSS enables rapid, responsive UI development
- Component-based architecture follows React best practices

---

## Post-Design Constitution Re-Check

*Re-evaluated after Phase 1 (Design & Contracts) completion*

### ✅ Spec-Driven Development
- All design artifacts reference spec requirements
- Component structure maps to functional requirements (FR-001 to FR-018)
- Data model entities map to spec entities
- No implementation without specification

### ✅ Security-First Design
- JWT tokens in httpOnly cookies (XSS protection)
- Protected routes enforce authentication
- API client includes token in all requests
- User data isolation enforced (only show user's tasks)
- Environment variables for sensitive config

### ✅ Deterministic Behavior
- API client produces consistent requests
- UI state transitions are predictable
- Error handling is standardized
- Form validation is consistent

### ✅ Separation of Concerns
- Pages handle routing and layout
- Components handle UI rendering
- API client handles backend communication
- Better Auth handles authentication
- Clear boundaries between layers

### ✅ Auditability
- All design decisions documented in research.md
- API client interface defined in contracts/
- Data model documents UI state and entities
- Quickstart provides implementation traceability

### ✅ Test-First Development
- Component tests defined for UI elements
- Integration tests for user journeys
- E2E tests for critical flows
- TDD cycle ready for implementation phase

### ✅ Independent User Stories
- P1 (auth UI) can be implemented and tested independently
- P2 (task management) builds on P1 but is independently testable
- P3 (session persistence) builds on P1 but is independently testable
- Each story delivers standalone value

### ✅ API-First Design
- Backend API contracts already defined
- Frontend API client follows REST conventions
- Request/response types fully specified
- Error responses standardized

**Final Gate Status**: ✅ PASS - All constitution principles satisfied after design phase

**Ready for**: `/sp.tasks` command to generate task breakdown
