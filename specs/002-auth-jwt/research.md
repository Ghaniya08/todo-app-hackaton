# Research: Authentication & User Context

**Feature**: 002-auth-jwt
**Date**: 2026-02-08
**Purpose**: Resolve technical unknowns and document best practices for authentication implementation

## Research Questions

### 1. Better Auth Integration with Next.js App Router

**Question**: How should Better Auth be configured for Next.js 16+ with App Router to issue JWT tokens?

**Research Findings**:
- Better Auth supports Next.js App Router with server-side session management
- Configuration requires auth.ts file in lib/ directory
- JWT tokens can be configured as the session strategy
- Better Auth handles password hashing automatically (bcrypt by default)
- Supports both httpOnly cookies and custom token storage

**Decision**: Use Better Auth with JWT session strategy
- Configure in `src/lib/auth.ts`
- Use httpOnly cookies for token storage (more secure than localStorage)
- Better Auth will handle signup, signin, and token issuance
- Frontend will automatically include cookies in API requests

**Rationale**: Better Auth provides secure defaults and reduces implementation complexity. httpOnly cookies prevent XSS attacks on tokens.

**Alternatives Considered**:
- Custom JWT implementation: Rejected due to security complexity
- NextAuth.js: Rejected as Better Auth is specified in requirements
- localStorage for tokens: Rejected due to XSS vulnerability

---

### 2. JWT Payload Structure

**Question**: What fields should be included in the JWT payload for backend verification?

**Research Findings**:
- Standard JWT claims: iss (issuer), sub (subject/user_id), exp (expiration), iat (issued at)
- Custom claims can include user metadata
- Payload should be minimal to reduce token size
- Backend needs user_id to enforce data isolation

**Decision**: JWT payload structure
```json
{
  "sub": "user_id_string",
  "email": "user@example.com",
  "iat": 1234567890,
  "exp": 1234654290
}
```

**Rationale**:
- `sub` contains user_id for backend filtering
- `email` for user identification in logs
- `iat` and `exp` for token validity verification
- Minimal payload reduces token size and improves performance

**Alternatives Considered**:
- Include user roles: Rejected as RBAC is out of scope
- Include user name: Rejected as not needed for authorization
- Include task IDs: Rejected as violates stateless principle

---

### 3. JWT Verification in FastAPI

**Question**: What is the best pattern for JWT verification middleware in FastAPI?

**Research Findings**:
- FastAPI supports dependency injection for middleware
- PyJWT library provides secure token verification
- Middleware should verify signature, expiration, and extract user_id
- Use `Depends()` to inject authenticated user into route handlers

**Decision**: Implement JWT verification as FastAPI dependency
```python
from fastapi import Depends, HTTPException, Header
import jwt

async def verify_jwt(authorization: str = Header(None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")

    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload["sub"]  # Return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

**Rationale**: Dependency injection is idiomatic FastAPI pattern. Provides clean separation and reusability.

**Alternatives Considered**:
- Global middleware: Rejected as some endpoints (auth) don't need verification
- Decorator pattern: Rejected as less idiomatic in FastAPI
- Manual verification in each route: Rejected due to code duplication

---

### 4. Token Expiration and Refresh Strategy

**Question**: How long should JWT tokens be valid, and do we need refresh tokens?

**Research Findings**:
- Industry standard: 15 minutes to 24 hours for access tokens
- Refresh tokens add complexity but improve security
- Spec specifies 24-hour validity
- Refresh token rotation is explicitly out of scope

**Decision**: 24-hour JWT token validity, no refresh tokens
- Tokens expire after 24 hours
- Users must sign in again after expiration
- No refresh token mechanism (out of scope per spec)

**Rationale**: Balances security and user experience. 24-hour validity reduces sign-in friction while limiting exposure window. Refresh tokens are explicitly out of scope.

**Alternatives Considered**:
- 15-minute tokens with refresh: Rejected as out of scope
- 7-day tokens: Rejected as too long for security
- Sliding expiration: Rejected as adds complexity

---

### 5. Password Hashing Algorithm

**Question**: Which password hashing algorithm should be used for user accounts?

**Research Findings**:
- bcrypt is industry standard for password hashing
- Argon2 is newer and more secure but less widely supported
- Better Auth uses bcrypt by default
- Python passlib library supports multiple algorithms

**Decision**: Use bcrypt for password hashing
- Better Auth handles hashing automatically on frontend
- Backend will verify hashed passwords from database
- Use bcrypt cost factor of 12 (secure and performant)

**Rationale**: bcrypt is battle-tested, widely supported, and Better Auth default. No need to override.

**Alternatives Considered**:
- Argon2: Rejected due to Better Auth default being bcrypt
- PBKDF2: Rejected as bcrypt is more secure
- Plain SHA-256: Rejected as insecure for passwords

---

### 6. User ID Format and Generation

**Question**: What format should user IDs use, and how should they be generated?

**Research Findings**:
- UUIDs provide uniqueness without coordination
- Auto-incrementing integers are simpler but reveal user count
- Better Auth generates user IDs automatically
- Backend needs to accept string user IDs

**Decision**: Use Better Auth generated user IDs (UUIDs)
- Better Auth generates unique user IDs on signup
- Backend accepts user_id as string type
- Database stores user_id as VARCHAR/TEXT

**Rationale**: Better Auth handles ID generation securely. UUIDs prevent enumeration attacks.

**Alternatives Considered**:
- Auto-increment integers: Rejected due to enumeration risk
- Custom ID generation: Rejected as Better Auth handles it
- Email as user ID: Rejected as users may change email

---

### 7. Token Storage Strategy (Frontend)

**Question**: Should JWT tokens be stored in httpOnly cookies or localStorage?

**Research Findings**:
- httpOnly cookies: Immune to XSS, vulnerable to CSRF
- localStorage: Vulnerable to XSS, immune to CSRF
- Better Auth supports both strategies
- CSRF protection can be added with tokens

**Decision**: Use httpOnly cookies for JWT storage
- Better Auth configured to use httpOnly cookies
- Cookies automatically included in API requests
- CSRF protection via SameSite=Strict attribute

**Rationale**: httpOnly cookies provide better security against XSS attacks, which are more common than CSRF in modern SPAs.

**Alternatives Considered**:
- localStorage: Rejected due to XSS vulnerability
- sessionStorage: Rejected as tokens lost on tab close
- Memory only: Rejected as tokens lost on page refresh

---

### 8. User Isolation Enforcement Strategy

**Question**: At what layers should user isolation be enforced?

**Research Findings**:
- Defense in depth: Multiple layers of protection
- Database queries should filter by user_id
- API routes should verify ownership
- Middleware should extract authenticated user

**Decision**: Multi-layer user isolation
1. **Middleware layer**: Extract user_id from JWT
2. **Route layer**: Verify URL user_id matches authenticated user_id
3. **Service layer**: Filter all database queries by user_id
4. **Database layer**: Add user_id to all task queries

**Rationale**: Defense in depth prevents security bypasses. Each layer provides independent protection.

**Alternatives Considered**:
- Database-only filtering: Rejected as insufficient
- Route-only verification: Rejected as can be bypassed
- Single-layer protection: Rejected as violates security best practices

---

## Technology Stack Decisions

### Frontend Dependencies
- **better-auth**: ^1.0.0 (authentication library)
- **@better-auth/react**: ^1.0.0 (React hooks)
- **next**: ^16.0.0 (existing)
- **typescript**: ^5.0.0 (existing)

### Backend Dependencies
- **PyJWT**: ^2.8.0 (JWT encoding/decoding)
- **passlib[bcrypt]**: ^1.7.4 (password hashing)
- **python-jose[cryptography]**: ^3.3.0 (alternative JWT library)
- **fastapi**: ^0.109.0 (existing)
- **sqlmodel**: ^0.0.14 (existing)

**Decision**: Use PyJWT for backend JWT verification
- Lightweight and focused on JWT only
- Well-maintained and widely used
- Simpler than python-jose for our use case

---

## Implementation Patterns

### Frontend Auth Flow
1. User submits signup/signin form
2. Better Auth validates credentials
3. Better Auth creates user account (signup) or verifies password (signin)
4. Better Auth issues JWT token in httpOnly cookie
5. Frontend redirects to dashboard
6. All API requests automatically include cookie

### Backend Auth Flow
1. Request arrives with Authorization header or cookie
2. JWT middleware extracts token
3. Middleware verifies signature using shared secret
4. Middleware decodes payload and extracts user_id
5. Middleware injects user_id into request context
6. Route handler receives authenticated user_id
7. Route handler verifies URL user_id matches authenticated user_id
8. Service layer filters database queries by user_id

### Error Handling
- 401 Unauthorized: Missing or invalid token
- 403 Forbidden: Valid token but accessing another user's resource
- 400 Bad Request: Invalid signup/signin data
- 409 Conflict: Email already exists (signup)

---

## Security Considerations

### Shared Secret Management
- Environment variable: BETTER_AUTH_SECRET
- Must be identical on frontend and backend
- Minimum 32 characters, cryptographically random
- Never committed to version control
- Rotated periodically in production

### Token Security
- Tokens signed with HS256 algorithm
- Signature prevents tampering
- Expiration prevents indefinite use
- httpOnly cookies prevent XSS access

### Password Security
- Passwords hashed with bcrypt (cost factor 12)
- Never stored or transmitted in plain text
- Better Auth handles hashing automatically
- Minimum password length: 8 characters (Better Auth default)

---

## Testing Strategy

### Contract Tests
- POST /api/auth/signup with valid data → 201 Created
- POST /api/auth/signup with existing email → 409 Conflict
- POST /api/auth/signin with correct credentials → 200 OK with token
- POST /api/auth/signin with wrong password → 401 Unauthorized
- GET /api/{user_id}/tasks without token → 401 Unauthorized
- GET /api/{user_id}/tasks with valid token → 200 OK
- GET /api/{other_user_id}/tasks with valid token → 403 Forbidden

### Integration Tests
- User signup → signin → create task → verify task visible
- User A creates task → User B cannot see User A's task
- Token expiration → request fails → user must sign in again

### Unit Tests
- JWT middleware extracts user_id correctly
- JWT middleware rejects expired tokens
- JWT middleware rejects invalid signatures
- Password hashing produces different hashes for same password

---

## Open Questions Resolved

All technical unknowns have been resolved:
- ✅ Better Auth integration pattern defined
- ✅ JWT payload structure decided
- ✅ Token expiration duration set (24 hours)
- ✅ Password hashing algorithm chosen (bcrypt)
- ✅ User ID format decided (Better Auth UUIDs)
- ✅ Token storage strategy selected (httpOnly cookies)
- ✅ User isolation enforcement layers defined

**Ready for Phase 1**: Data model and API contracts can now be generated.
