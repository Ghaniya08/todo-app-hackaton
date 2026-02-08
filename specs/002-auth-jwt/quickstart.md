# Quickstart: Authentication & User Context

**Feature**: 002-auth-jwt
**Date**: 2026-02-08
**Purpose**: Step-by-step guide for implementing authentication

## Prerequisites

- Backend API from Phase I (001-backend-task-api) running
- Node.js 18+ and Python 3.13+ installed
- Neon PostgreSQL database configured
- Git repository initialized

## Implementation Order

Follow this sequence to implement authentication:

### Phase 1: Backend Authentication (Priority: P1)

**Goal**: Secure backend API with JWT verification

**Steps**:

1. **Install Dependencies**
   ```bash
   cd backend
   pip install PyJWT==2.8.0 passlib[bcrypt]==1.7.4
   ```

2. **Create User Model** (`backend/src/models/user.py`)
   - Define User SQLModel with id, email, password_hash, name, timestamps
   - Add validation for email format and uniqueness
   - Reference: `specs/002-auth-jwt/data-model.md`

3. **Create Auth Service** (`backend/src/services/auth_service.py`)
   - Implement `create_user(email, password, name)` → hash password, create user
   - Implement `verify_password(email, password)` → check hash, return user
   - Implement `generate_jwt(user_id)` → create JWT token with 24h expiration
   - Use bcrypt for password hashing (cost factor 12)

4. **Create JWT Middleware** (`backend/src/middleware/jwt_auth.py`)
   - Implement `verify_jwt(authorization: str)` dependency
   - Extract token from Authorization header or cookie
   - Verify signature using BETTER_AUTH_SECRET
   - Decode payload and return user_id
   - Raise HTTPException(401) for invalid/expired tokens

5. **Create Auth Routes** (`backend/src/routes/auth.py`)
   - POST /api/auth/signup → create user, return JWT
   - POST /api/auth/signin → verify credentials, return JWT
   - POST /api/auth/signout → clear cookie
   - GET /api/auth/me → return current user info
   - Reference: `specs/002-auth-jwt/contracts/auth-api.yaml`

6. **Update Configuration** (`backend/src/config.py`)
   - Add `better_auth_secret` from environment variable
   - Validate secret is at least 32 characters

7. **Update Environment** (`backend/.env`)
   ```
   BETTER_AUTH_SECRET=your-32-character-secret-here
   DATABASE_URL=postgresql+psycopg://...
   ```

8. **Register Auth Routes** (`backend/src/main.py`)
   - Import and include auth router
   - Add CORS middleware with credentials support

9. **Create Database Migration**
   - Run SQL to create users table
   - Add foreign key from tasks.user_id to users.id
   - Reference: `specs/002-auth-jwt/data-model.md`

10. **Write Tests** (`backend/tests/contract/test_auth_api.py`)
    - Test signup with valid data → 201
    - Test signup with existing email → 409
    - Test signin with correct credentials → 200
    - Test signin with wrong password → 401
    - Reference: `specs/002-auth-jwt/contracts/auth-api.yaml`

**Acceptance Criteria**:
- ✅ Users can sign up with email and password
- ✅ Users can sign in and receive JWT token
- ✅ Invalid credentials return 401 error
- ✅ Duplicate email returns 409 error

---

### Phase 2: Secure Task Endpoints (Priority: P2)

**Goal**: Enforce user isolation on all task operations

**Steps**:

1. **Update Task Routes** (`backend/src/routes/tasks.py`)
   - Add `user_id: str = Depends(verify_jwt)` to all endpoints
   - Verify URL user_id matches authenticated user_id
   - Raise HTTPException(403) if mismatch
   - Pass authenticated user_id to service layer

2. **Update Task Service** (`backend/src/services/task_service.py`)
   - Add user_id parameter to all methods
   - Filter all database queries by user_id
   - Ensure created tasks have correct user_id

3. **Update Task Tests** (`backend/tests/contract/test_task_api.py`)
   - Add Authorization header to all requests
   - Test accessing another user's task → 403
   - Test without token → 401

4. **Create User Isolation Tests** (`backend/tests/integration/test_user_isolation.py`)
   - Create two users (Alice, Bob)
   - Alice creates task → Bob cannot see it
   - Alice tries to access Bob's task → 403
   - Reference: `specs/002-auth-jwt/data-model.md` (Test Scenarios)

**Acceptance Criteria**:
- ✅ All task endpoints require valid JWT
- ✅ Users only see their own tasks
- ✅ Accessing another user's task returns 403
- ✅ Missing token returns 401

---

### Phase 3: Frontend Authentication (Priority: P1)

**Goal**: Implement signup/signin UI with Better Auth

**Steps**:

1. **Install Dependencies**
   ```bash
   cd frontend
   npm install better-auth @better-auth/react
   ```

2. **Configure Better Auth** (`frontend/src/lib/auth.ts`)
   - Initialize Better Auth with JWT strategy
   - Configure httpOnly cookies
   - Set token expiration to 24 hours
   - Use BETTER_AUTH_SECRET from environment

3. **Create Auth Components**
   - `frontend/src/components/auth/SignUpForm.tsx` → signup form
   - `frontend/src/components/auth/SignInForm.tsx` → signin form
   - Handle form validation and error display

4. **Create Auth Pages**
   - `frontend/src/app/(auth)/signup/page.tsx` → signup page
   - `frontend/src/app/(auth)/signin/page.tsx` → signin page
   - Redirect to dashboard on success

5. **Update API Client** (`frontend/src/lib/api.ts`)
   - Configure to include credentials (cookies) in requests
   - Add error handling for 401 (redirect to signin)
   - Add error handling for 403 (show permission error)

6. **Add Route Protection** (`frontend/src/middleware.ts`)
   - Check for valid JWT token
   - Redirect unauthenticated users to signin
   - Allow public access to auth pages

7. **Update Layout** (`frontend/src/app/layout.tsx`)
   - Wrap app with Better Auth provider
   - Add auth context for components

8. **Update Environment** (`frontend/.env.local`)
   ```
   BETTER_AUTH_SECRET=your-32-character-secret-here
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

**Acceptance Criteria**:
- ✅ Users can sign up from UI
- ✅ Users can sign in from UI
- ✅ JWT token stored in httpOnly cookie
- ✅ Unauthenticated users redirected to signin

---

### Phase 4: Session Persistence (Priority: P3)

**Goal**: Maintain user sessions across page navigations

**Steps**:

1. **Implement Session Check** (`frontend/src/lib/auth.ts`)
   - Check for valid token on app load
   - Restore user session if token valid
   - Clear session if token expired

2. **Add Session Context** (`frontend/src/app/layout.tsx`)
   - Provide current user to all components
   - Handle session expiration gracefully

3. **Update Dashboard** (`frontend/src/app/dashboard/page.tsx`)
   - Display current user information
   - Add sign out button
   - Show loading state while checking session

4. **Handle Token Expiration**
   - Detect 401 responses from API
   - Clear local session
   - Redirect to signin with message

**Acceptance Criteria**:
- ✅ Users remain signed in across page refreshes
- ✅ Users remain signed in after closing browser (within 24h)
- ✅ Expired tokens trigger re-authentication
- ✅ Sign out clears session properly

---

## Testing Checklist

### Backend Tests

- [ ] POST /api/auth/signup with valid data → 201 Created
- [ ] POST /api/auth/signup with existing email → 409 Conflict
- [ ] POST /api/auth/signin with correct credentials → 200 OK
- [ ] POST /api/auth/signin with wrong password → 401 Unauthorized
- [ ] GET /api/{user_id}/tasks without token → 401 Unauthorized
- [ ] GET /api/{user_id}/tasks with valid token → 200 OK
- [ ] GET /api/{other_user_id}/tasks with valid token → 403 Forbidden
- [ ] POST /api/{user_id}/tasks creates task with correct user_id
- [ ] User A cannot see User B's tasks
- [ ] User A cannot modify User B's tasks

### Frontend Tests

- [ ] Signup form validates email format
- [ ] Signup form validates password length
- [ ] Successful signup redirects to dashboard
- [ ] Signin form handles incorrect credentials
- [ ] Successful signin redirects to dashboard
- [ ] Dashboard shows current user information
- [ ] Sign out clears session and redirects to signin
- [ ] Protected routes redirect unauthenticated users
- [ ] Session persists across page refresh
- [ ] Expired token triggers re-authentication

### Integration Tests

- [ ] End-to-end: Signup → Signin → Create Task → View Task
- [ ] End-to-end: User A creates task → User B cannot see it
- [ ] End-to-end: Token expiration → Re-signin required
- [ ] End-to-end: Sign out → Cannot access protected routes

---

## Common Issues and Solutions

### Issue: "Invalid token signature"
**Cause**: BETTER_AUTH_SECRET mismatch between frontend and backend
**Solution**: Ensure both .env files have identical BETTER_AUTH_SECRET value

### Issue: "CORS error when calling API"
**Cause**: Backend not configured to accept credentials
**Solution**: Add `credentials: true` to CORS middleware in backend/src/main.py

### Issue: "Token not included in requests"
**Cause**: API client not configured to send cookies
**Solution**: Add `credentials: 'include'` to fetch options in frontend/src/lib/api.ts

### Issue: "User can access another user's tasks"
**Cause**: Missing user_id verification in route handler
**Solution**: Verify URL user_id matches authenticated user_id from JWT

### Issue: "Password hash verification fails"
**Cause**: Incorrect bcrypt configuration
**Solution**: Ensure Better Auth and backend use same bcrypt cost factor (12)

---

## Environment Variables Reference

### Backend (.env)
```bash
DATABASE_URL=postgresql+psycopg://user:pass@host/db?sslmode=require
BETTER_AUTH_SECRET=your-32-character-secret-here
ENVIRONMENT=development
LOG_LEVEL=info
```

### Frontend (.env.local)
```bash
BETTER_AUTH_SECRET=your-32-character-secret-here
NEXT_PUBLIC_API_URL=http://localhost:8000
NODE_ENV=development
```

**CRITICAL**: BETTER_AUTH_SECRET must be identical in both files!

---

## Deployment Checklist

- [ ] Generate secure BETTER_AUTH_SECRET (32+ characters)
- [ ] Configure environment variables on hosting platform
- [ ] Verify CORS allows frontend domain
- [ ] Test authentication flow in production
- [ ] Verify JWT tokens work across frontend/backend
- [ ] Test user isolation with multiple accounts
- [ ] Confirm session persistence works
- [ ] Test token expiration handling

---

## Next Steps

After completing authentication:
1. Run `/sp.tasks` to generate task breakdown
2. Implement tasks in priority order (P1 → P2 → P3)
3. Test each user story independently
4. Create PHR for implementation work
5. Proceed to frontend UI development (if not done in parallel)

---

## References

- **Specification**: `specs/002-auth-jwt/spec.md`
- **Implementation Plan**: `specs/002-auth-jwt/plan.md`
- **Research**: `specs/002-auth-jwt/research.md`
- **Data Model**: `specs/002-auth-jwt/data-model.md`
- **API Contracts**: `specs/002-auth-jwt/contracts/`
- **Constitution**: `.specify/memory/constitution.md`
