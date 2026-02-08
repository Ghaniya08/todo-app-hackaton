# Data Model: Frontend UI & Integration

**Feature**: 003-frontend-ui | **Date**: 2026-02-08 | **Spec**: [spec.md](./spec.md)

## Overview

This document defines the data entities and state management for the frontend application. The frontend consumes the backend REST API and manages UI state locally using React's built-in state management.

## Entity Definitions

### 1. User Session (Authentication State)

Represents an authenticated user's session managed by Better Auth.

**Source**: Better Auth Context + JWT token in httpOnly cookie

**Properties**:
```typescript
interface UserSession {
  user: {
    id: string              // Unique user identifier (UUID from backend)
    email: string           // User's email address
    name: string            // User's display name
  }
  token: string             // JWT token (managed by Better Auth, not directly accessible)
  isAuthenticated: boolean  // Authentication status
  isLoading: boolean        // Session initialization loading state
}
```

**Lifecycle**:
- Created: On successful signup or signin
- Updated: Never (immutable during session)
- Destroyed: On signout or token expiration
- Persisted: JWT token in httpOnly cookie (24-hour expiration)

**Access Pattern**:
- Read: Via Better Auth `useSession()` hook
- Write: Via Better Auth `signIn()`, `signUp()`, `signOut()` methods
- Validation: Automatic via Better Auth middleware

**Related User Stories**: US1 (Authentication Flow), US3 (Session Persistence)

---

### 2. Task (Todo Item)

Represents a todo item owned by a user.

**Source**: Backend API (`/api/{user_id}/tasks`)

**Properties**:
```typescript
interface Task {
  id: number                // Unique task identifier (auto-increment from backend)
  user_id: string           // Owner's user ID (foreign key to users table)
  title: string             // Task title (max 200 chars, required)
  description: string | null // Task description (max 1000 chars, optional)
  completed: boolean        // Completion status (default: false)
  created_at: string        // ISO 8601 timestamp (UTC)
  updated_at: string        // ISO 8601 timestamp (UTC)
}
```

**Validation Rules**:
- `title`: Required, 1-200 characters, non-empty after trim
- `description`: Optional, max 1000 characters
- `completed`: Boolean, defaults to false
- `user_id`: Must match authenticated user's ID

**Lifecycle**:
- Created: POST `/api/{user_id}/tasks` with `TaskCreate` payload
- Read: GET `/api/{user_id}/tasks` (list) or GET `/api/{user_id}/tasks/{id}` (single)
- Updated: PUT `/api/{user_id}/tasks/{id}` with `TaskUpdate` payload
- Completed: PATCH `/api/{user_id}/tasks/{id}/complete` (toggle)
- Deleted: DELETE `/api/{user_id}/tasks/{id}`

**Access Pattern**:
- Fetched on dashboard mount
- Cached in component state (useState)
- Optimistic updates for better UX
- Re-fetched after mutations

**Related User Stories**: US2 (Task Management Interface)

---

### 3. UI State (Component State)

Represents transient UI state for forms, modals, and loading indicators.

**Source**: React component state (useState, useReducer)

**Properties**:

#### 3.1 Form State (Task Creation/Editing)
```typescript
interface TaskFormState {
  title: string             // Current title input value
  description: string       // Current description input value
  errors: {
    title?: string          // Title validation error message
    description?: string    // Description validation error message
  }
  isSubmitting: boolean     // Form submission in progress
  isDirty: boolean          // Form has unsaved changes
}
```

#### 3.2 Loading State
```typescript
interface LoadingState {
  isLoadingTasks: boolean   // Task list fetch in progress
  isCreatingTask: boolean   // Task creation in progress
  isUpdatingTask: number | null  // Task ID being updated (null if none)
  isDeletingTask: number | null  // Task ID being deleted (null if none)
  isTogglingTask: number | null  // Task ID being toggled (null if none)
}
```

#### 3.3 Error State
```typescript
interface ErrorState {
  message: string | null    // User-friendly error message
  type: 'auth' | 'network' | 'validation' | 'server' | null
  retryAction?: () => void  // Optional retry callback
}
```

#### 3.4 Modal State
```typescript
interface ModalState {
  isOpen: boolean           // Modal visibility
  mode: 'create' | 'edit' | null  // Modal mode
  taskId?: number           // Task ID for edit mode
}
```

**Lifecycle**:
- Created: On component mount or user interaction
- Updated: On user input or API response
- Destroyed: On component unmount or modal close
- Persisted: Never (transient state only)

**Access Pattern**:
- Local to component (useState)
- Passed down via props where needed
- No global state management

**Related User Stories**: US2 (Task Management), US3 (Error Handling)

---

## State Management Strategy

### React Built-in State Management

**Global State** (Better Auth Context):
- User session (authentication state)
- Provided by Better Auth `<SessionProvider>`
- Accessed via `useSession()` hook

**Local State** (Component useState):
- Task list (dashboard page)
- Form inputs (task forms)
- Loading indicators (per operation)
- Error messages (per component)
- Modal visibility (task forms)

**No Redux/Zustand/Jotai** - React's built-in state is sufficient for this application's complexity.

---

## API Request/Response Types

### Request Payloads

#### TaskCreate (POST /api/{user_id}/tasks)
```typescript
interface TaskCreate {
  title: string             // Required, 1-200 chars
  description?: string      // Optional, max 1000 chars
}
```

#### TaskUpdate (PUT /api/{user_id}/tasks/{id})
```typescript
interface TaskUpdate {
  title?: string            // Optional, 1-200 chars if provided
  description?: string      // Optional, max 1000 chars if provided
  completed?: boolean       // Optional, toggle completion
}
```

### Response Payloads

#### Task (Single)
```typescript
interface TaskResponse {
  id: number
  user_id: string
  title: string
  description: string | null
  completed: boolean
  created_at: string
  updated_at: string
}
```

#### TaskList (Array)
```typescript
type TaskListResponse = TaskResponse[]
```

#### Error Response
```typescript
interface ErrorResponse {
  detail: string            // User-friendly error message
  status_code: number       // HTTP status code
}
```

---

## Data Flow Diagrams

### Authentication Flow
```
User Input (email, password)
  ↓
Better Auth signIn()
  ↓
POST /api/auth/signin (Backend)
  ↓
JWT Token in httpOnly Cookie
  ↓
Better Auth Session Context
  ↓
Redirect to Dashboard
```

### Task Creation Flow
```
User Input (title, description)
  ↓
Form Validation (React Hook Form + Zod)
  ↓
API Client POST /api/{user_id}/tasks
  ↓
Backend Creates Task
  ↓
Task Response
  ↓
Update Local State (useState)
  ↓
Re-render Task List
```

### Task List Fetch Flow
```
Dashboard Mount
  ↓
API Client GET /api/{user_id}/tasks
  ↓
Backend Filters by user_id
  ↓
Task List Response
  ↓
Update Local State (useState)
  ↓
Render Task List
```

---

## Validation Rules

### Client-Side Validation (React Hook Form + Zod)

**Task Title**:
- Required: "Title is required"
- Min length: 1 character (after trim)
- Max length: 200 characters
- Pattern: Non-empty after trim

**Task Description**:
- Optional
- Max length: 1000 characters

**Email (Signup/Signin)**:
- Required: "Email is required"
- Format: Valid email format
- Pattern: `/^[^\s@]+@[^\s@]+\.[^\s@]+$/`

**Password (Signup/Signin)**:
- Required: "Password is required"
- Min length: 8 characters
- Pattern: At least one letter and one number (enforced by backend)

### Server-Side Validation (Backend - Final Authority)

All client-side validation is duplicated on the backend for security. The backend is the final authority for all validation rules.

---

## Error Handling Strategy

### Error Types and User Messages

| Error Type | HTTP Status | User Message | Action |
|------------|-------------|--------------|--------|
| AuthenticationError | 401 | "Your session has expired. Please sign in again." | Redirect to signin |
| AuthorizationError | 403 | "You don't have permission to perform this action." | Show error message |
| ValidationError | 400 | Field-specific errors (e.g., "Title is required") | Show inline errors |
| NetworkError | - | "Network error. Please check your connection and try again." | Show retry button |
| ServerError | 500 | "Something went wrong. Please try again later." | Show retry button |

### Error Recovery

- **Transient Errors** (network, 500): Provide retry button
- **Permanent Errors** (401, 403): Redirect or show message
- **Validation Errors** (400): Show inline field errors

---

## Performance Considerations

### Data Fetching
- Task list fetched once on dashboard mount
- No polling or real-time updates (Phase III feature)
- Optimistic updates for better perceived performance

### Caching
- No client-side caching (always fetch fresh data)
- Browser cache for static assets only

### Bundle Size
- Better Auth: ~20KB
- React Hook Form: ~25KB
- Zod: ~15KB
- Total JS bundle target: <200KB (gzipped)

---

## Security Considerations

### JWT Token Handling
- Tokens stored in httpOnly cookies (not accessible to JavaScript)
- Cookies have Secure flag (HTTPS only in production)
- Cookies have SameSite=Strict (CSRF protection)
- Tokens automatically included in API requests
- No manual token management in frontend code

### User Data Isolation
- Frontend displays only authenticated user's tasks
- Backend enforces user isolation (defense in depth)
- All API requests include user_id in URL path
- Backend verifies token user_id matches URL user_id

### Input Sanitization
- React automatically escapes all rendered content (XSS protection)
- No use of `dangerouslySetInnerHTML`
- All user input validated before submission

---

## Testing Strategy

### Unit Tests (Jest + Testing Library)
- Component rendering with mock data
- Form validation logic
- API client error handling
- Utility functions

### Integration Tests
- User journey: Signup → Signin → Create Task → Complete Task → Delete Task
- Authentication flow: Signin → Protected route → Signout
- Error handling: Network error → Retry → Success

### E2E Tests (Playwright)
- Critical user flows
- Cross-browser testing (Chrome, Firefox, Safari)
- Mobile responsive testing (320px to desktop)

---

## Related Documents

- [spec.md](./spec.md) - Feature specification with user stories
- [plan.md](./plan.md) - Implementation plan and technical context
- [research.md](./research.md) - Technical research and decisions
- [contracts/api-client.ts](./contracts/api-client.ts) - TypeScript API client interface
- [quickstart.md](./quickstart.md) - Implementation guide

---

**Status**: ✅ Complete - Ready for task breakdown (`/sp.tasks`)
