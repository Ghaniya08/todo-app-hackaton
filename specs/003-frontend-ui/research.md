# Research: Frontend UI & Integration

**Feature**: 003-frontend-ui
**Date**: 2026-02-08
**Purpose**: Resolve technical unknowns and document best practices for frontend implementation

## Research Questions

### 1. Better Auth vs NextAuth.js for Next.js 16+ App Router

**Question**: Which authentication library should be used for JWT-based authentication in Next.js 16+ App Router?

**Research Findings**:
- Better Auth is a newer library specifically designed for modern Next.js with App Router support
- NextAuth.js (now Auth.js) is more mature but has some App Router compatibility issues
- Better Auth provides simpler JWT token management with httpOnly cookies
- Better Auth has built-in TypeScript support and better DX for App Router
- Backend already uses JWT tokens with HS256 signature - need frontend library that can consume these

**Decision**: Use Better Auth for frontend authentication
- Native App Router support (Server Components, Route Handlers)
- Simpler JWT token handling with httpOnly cookies
- Can consume existing backend JWT tokens
- TypeScript-first design
- Smaller bundle size than NextAuth.js

**Rationale**: Better Auth is purpose-built for Next.js App Router and provides the simplest integration path with our existing JWT-based backend. It handles httpOnly cookies automatically and has excellent TypeScript support.

**Alternatives Considered**:
- NextAuth.js: Rejected due to App Router compatibility issues and complexity
- Custom JWT implementation: Rejected due to security complexity and reinventing the wheel
- Clerk/Auth0: Rejected as they require their own backend (we already have one)

---

### 2. API Client Architecture

**Question**: How should the frontend communicate with the backend API?

**Research Findings**:
- Native fetch API is sufficient for REST calls
- Need to handle JWT token attachment automatically
- Need centralized error handling for 401/403 responses
- Need request/response type safety with TypeScript
- Backend API base URL should be configurable via environment variable

**Decision**: Create custom API client wrapper around fetch
```typescript
// lib/api.ts structure
- Base fetch wrapper with JWT token attachment
- Typed request/response interfaces
- Centralized error handling
- Automatic retry for network errors
- Request/response interceptors
```

**Rationale**: Custom wrapper provides full control over request/response handling while keeping it simple. Native fetch is sufficient - no need for heavy libraries like Axios.

**Alternatives Considered**:
- Axios: Rejected as unnecessary dependency (fetch is sufficient)
- SWR/React Query: Deferred to future enhancement (adds complexity)
- tRPC: Rejected as backend is REST, not tRPC

---

### 3. State Management Strategy

**Question**: How should UI state be managed across components?

**Research Findings**:
- React 18+ has built-in state management (useState, useContext)
- Next.js App Router supports Server Components (no client state)
- Authentication state needs to be global (Better Auth provides this)
- Task list state can be local to dashboard page
- Form state can be local to form components

**Decision**: Use React built-in state management
- Better Auth Context for authentication state
- Local useState for component state (forms, modals)
- Server Components for static content
- Client Components only where interactivity needed

**Rationale**: Built-in React state is sufficient for this application's complexity. No need for Redux/Zustand/Jotai. Keeps bundle size small and code simple.

**Alternatives Considered**:
- Redux: Rejected as overkill for this application
- Zustand: Rejected as unnecessary (React Context sufficient)
- Jotai/Recoil: Rejected as adds complexity without benefit

---

### 4. Styling Approach

**Question**: How should the UI be styled?

**Research Findings**:
- Tailwind CSS is industry standard for utility-first styling
- Provides responsive design utilities out of the box
- Excellent TypeScript support with IntelliSense
- Small production bundle (only used classes included)
- Fast development with utility classes

**Decision**: Use Tailwind CSS for styling
- Utility-first approach for rapid development
- Built-in responsive design utilities
- Dark mode support (future enhancement)
- Component variants with class composition

**Rationale**: Tailwind CSS provides the fastest path to responsive, professional UI without writing custom CSS. Industry standard with excellent documentation.

**Alternatives Considered**:
- CSS Modules: Rejected as more verbose than Tailwind
- Styled Components: Rejected as adds runtime overhead
- Plain CSS: Rejected as requires more custom code

---

### 5. Form Validation Strategy

**Question**: How should form inputs be validated?

**Research Findings**:
- React Hook Form is lightweight and performant
- Zod provides TypeScript-first schema validation
- Better Auth has built-in validation for auth forms
- Backend already validates on API level (defense in depth)

**Decision**: Use React Hook Form + Zod for form validation
- React Hook Form for form state management
- Zod for schema validation (matches TypeScript types)
- Client-side validation for UX (immediate feedback)
- Backend validation as final authority

**Rationale**: React Hook Form + Zod provides excellent DX with TypeScript integration. Lightweight and performant. Zod schemas can be shared between frontend and backend.

**Alternatives Considered**:
- Formik: Rejected as heavier than React Hook Form
- Manual validation: Rejected as error-prone and verbose
- Yup: Rejected in favor of Zod (better TypeScript support)

---

### 6. Error Handling Strategy

**Question**: How should API errors be handled and displayed to users?

**Research Findings**:
- Backend returns consistent error format (HTTPException with detail)
- Need to map HTTP status codes to user-friendly messages
- Need to handle network errors separately from API errors
- Need to provide retry mechanism for transient failures

**Decision**: Centralized error handling in API client
```typescript
Error types:
- AuthenticationError (401) → Redirect to signin
- AuthorizationError (403) → Show permission error
- ValidationError (400) → Show field-specific errors
- NetworkError → Show retry option
- ServerError (500) → Show generic error with support contact
```

**Rationale**: Centralized error handling ensures consistent UX across the application. Users see helpful messages instead of technical errors.

**Alternatives Considered**:
- Component-level error handling: Rejected as leads to inconsistency
- Error boundaries only: Rejected as insufficient for API errors
- Toast notifications: Deferred to future enhancement

---

### 7. Loading State Strategy

**Question**: How should loading states be displayed during async operations?

**Research Findings**:
- Users expect feedback within 300ms for any operation
- Skeleton screens provide better UX than spinners for content loading
- Inline spinners work well for button actions
- Need to prevent duplicate submissions during loading

**Decision**: Multi-level loading indicators
- Skeleton screens for initial page load
- Inline spinners for button actions (submit, delete)
- Disabled state for forms during submission
- Loading prop passed to components

**Rationale**: Different loading patterns for different contexts provides the best UX. Skeleton screens feel faster than spinners for content.

**Alternatives Considered**:
- Global loading bar: Rejected as doesn't indicate what's loading
- Spinners everywhere: Rejected as less polished than skeletons
- No loading indicators: Rejected as poor UX

---

### 8. Routing and Navigation

**Question**: How should routing and navigation be structured?

**Research Findings**:
- Next.js App Router uses file-system based routing
- Route groups (auth) allow layout sharing without URL nesting
- Middleware can protect routes before rendering
- Server Components can check auth on server side

**Decision**: File-system routing with middleware protection
```
app/
├── (auth)/          # Route group for auth pages
│   ├── signin/
│   └── signup/
├── dashboard/       # Protected route
├── layout.tsx       # Root layout with auth provider
└── middleware.ts    # Route protection
```

**Rationale**: Next.js App Router conventions provide the simplest routing solution. Middleware protection ensures unauthenticated users can't access protected routes.

**Alternatives Considered**:
- Client-side route protection: Rejected as less secure (flash of content)
- React Router: Rejected as Next.js has built-in routing
- Manual route checking: Rejected as middleware is cleaner

---

## Technology Stack Decisions

### Frontend Dependencies
- **next**: ^16.0.0 (App Router, Server Components)
- **react**: ^18.0.0 (UI library)
- **typescript**: ^5.0.0 (Type safety)
- **better-auth**: ^1.0.0 (Authentication)
- **@better-auth/react**: ^1.0.0 (React hooks)
- **tailwindcss**: ^3.4.0 (Styling)
- **react-hook-form**: ^7.50.0 (Form management)
- **zod**: ^3.22.0 (Schema validation)

### Development Dependencies
- **@types/react**: ^18.0.0
- **@types/node**: ^20.0.0
- **eslint**: ^8.0.0
- **prettier**: ^3.0.0
- **jest**: ^29.0.0 (Unit tests)
- **@testing-library/react**: ^14.0.0 (Component tests)
- **playwright**: ^1.40.0 (E2E tests)

---

## Implementation Patterns

### Authentication Flow
1. User visits signin/signup page
2. Better Auth handles form submission
3. Backend validates credentials and returns JWT in httpOnly cookie
4. Frontend redirects to dashboard
5. Middleware checks for valid JWT on protected routes
6. API client includes JWT cookie in all requests

### API Request Flow
1. Component calls API client method
2. API client attaches JWT token from cookie
3. API client sends request to backend
4. Backend validates JWT and processes request
5. API client receives response
6. API client handles errors (401 → redirect, 403 → error message)
7. Component updates UI with response data

### Component Patterns
- **Server Components**: Static content, initial data fetching
- **Client Components**: Interactive elements (forms, buttons, modals)
- **Composition**: Small, reusable components composed into pages
- **Props drilling**: Minimal (use Context for global state)

---

## Security Considerations

### JWT Token Handling
- Tokens stored in httpOnly cookies (not accessible to JavaScript)
- Cookies have Secure flag (HTTPS only in production)
- Cookies have SameSite=Strict (CSRF protection)
- Tokens automatically included in API requests
- No manual token management in frontend code

### Input Validation
- Client-side validation for UX (immediate feedback)
- Backend validation as final authority (security)
- XSS prevention via React's automatic escaping
- No dangerouslySetInnerHTML usage

### Route Protection
- Middleware checks authentication before rendering
- Server Components can verify auth on server
- Unauthenticated users redirected to signin
- No protected content rendered before auth check

---

## Performance Optimizations

### Bundle Size
- Tree-shaking with ES modules
- Dynamic imports for large components
- Tailwind CSS purging (only used classes)
- Better Auth is lightweight (~20KB)

### Loading Performance
- Server Components for static content (no JS)
- Client Components only where needed
- Image optimization with Next.js Image
- Font optimization with Next.js Font

### Runtime Performance
- React 18 concurrent features
- Automatic code splitting by route
- Prefetching for navigation
- Optimistic UI updates for better perceived performance

---

## Testing Strategy

### Unit Tests (Jest + Testing Library)
- Component rendering tests
- Form validation tests
- Utility function tests
- API client tests (mocked fetch)

### Integration Tests
- User journey tests (signup → signin → create task)
- Authentication flow tests
- Error handling tests
- Loading state tests

### E2E Tests (Playwright)
- Critical user flows
- Cross-browser testing
- Mobile responsive testing
- Accessibility testing

---

## Open Questions Resolved

All technical unknowns have been resolved:
- ✅ Authentication library chosen (Better Auth)
- ✅ API client architecture defined
- ✅ State management strategy decided
- ✅ Styling approach selected (Tailwind CSS)
- ✅ Form validation strategy chosen (React Hook Form + Zod)
- ✅ Error handling strategy defined
- ✅ Loading state strategy decided
- ✅ Routing structure defined

**Ready for Phase 1**: Data model and API contracts can now be generated.
