---
description: "Task breakdown for Authentication & User Context implementation"
---

# Tasks: Authentication & User Context

**Input**: Design documents from `/specs/002-auth-jwt/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Test tasks are included per constitution requirement (Test-First Development is MANDATORY)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app structure**: `backend/src/`, `backend/tests/`, `frontend/src/`
- All paths are relative to repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency installation

- [x] T001 Install backend authentication dependencies in backend/requirements.txt (PyJWT==2.8.0, passlib[bcrypt]==1.7.4)
- [x] T002 [P] Update backend/.env.example with BETTER_AUTH_SECRET placeholder
- [x] T003 [P] Generate secure BETTER_AUTH_SECRET (32+ characters) and add to backend/.env
- [ ] T004 [P] Install frontend authentication dependencies (better-auth, @better-auth/react) in frontend/package.json
- [ ] T005 [P] Update frontend/.env.local with BETTER_AUTH_SECRET and NEXT_PUBLIC_API_URL

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core authentication infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T006 Create User SQLModel entity in backend/src/models/user.py (id, email, password_hash, name, created_at, updated_at per data-model.md)
- [x] T007 [P] Create Pydantic schemas in backend/src/schemas/user_schemas.py (UserCreate, UserResponse, SignInRequest per contracts/auth-api.yaml)
- [x] T008 Update backend/src/config.py to load BETTER_AUTH_SECRET from environment and validate minimum 32 characters
- [x] T009 Create database migration script in backend/migrations/ to create users table with indexes (email unique, created_at)
- [x] T010 Add foreign key constraint from tasks.user_id to users.id in migration script (ON DELETE CASCADE)
- [x] T011 Create JWT middleware in backend/src/middleware/jwt_auth.py (verify_jwt dependency: extract token, verify signature, decode payload, return user_id, raise 401 for invalid/expired)
- [x] T012 [P] Create pytest fixtures in backend/tests/conftest.py for test users, JWT tokens, and authenticated test client
- [x] T013 Update backend/src/main.py CORS middleware to allow credentials (credentials=True, allow_credentials=True)

**Checkpoint**: ✅ Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - User Registration and Sign-In (Priority: P1) 🎯 MVP

**Goal**: Users can create accounts and sign in to access the application

**Independent Test**: Create a new account via POST /api/auth/signup, sign out, then sign in via POST /api/auth/signin. Verify JWT token is issued and user information is returned.

**Acceptance Criteria** (from spec.md):
- User can sign up with valid email and password → 201 response with user details and JWT cookie
- User can sign in with correct credentials → 200 response with user details and JWT cookie
- Invalid credentials return 401 error with clear message
- Duplicate email returns 409 error

### Tests for User Story 1 (TDD - Write First, Ensure FAIL)

- [x] T014 [P] [US1] Write contract test for POST /api/auth/signup in backend/tests/contract/test_auth_api.py (test_signup_valid_data → 201, test_signup_existing_email → 409, test_signup_invalid_email → 400, test_signup_short_password → 400)
- [x] T015 [P] [US1] Write contract test for POST /api/auth/signin in backend/tests/contract/test_auth_api.py (test_signin_correct_credentials → 200, test_signin_wrong_password → 401, test_signin_nonexistent_email → 401, test_signin_missing_fields → 400)
- [x] T016 [P] [US1] Write contract test for POST /api/auth/signout in backend/tests/contract/test_auth_api.py (test_signout_authenticated → 200, test_signout_clears_cookie)
- [x] T017 [P] [US1] Write contract test for GET /api/auth/me in backend/tests/contract/test_auth_api.py (test_get_current_user_authenticated → 200, test_get_current_user_unauthenticated → 401)
- [x] T018 [P] [US1] Write integration test for User Story 1 in backend/tests/integration/test_user_stories.py (test_user_story_1_signup_and_signin: complete user journey from signup to signin)

**Checkpoint**: ✅ All US1 tests written and FAILING (red phase) - COMPLETE

### Implementation for User Story 1

- [x] T019 [US1] Implement AuthService.create_user() in backend/src/services/auth_service.py (validate email uniqueness, hash password with bcrypt cost 12, generate UUID, create user record, return user object)
- [x] T020 [US1] Implement AuthService.verify_password() in backend/src/services/auth_service.py (lookup user by email, verify password hash, return user object or None)
- [x] T021 [US1] Implement AuthService.generate_jwt() in backend/src/services/auth_service.py (create JWT with payload: sub=user_id, email, iat, exp=24h, sign with BETTER_AUTH_SECRET using HS256)
- [x] T022 [US1] Create auth router in backend/src/routes/auth.py (initialize APIRouter with prefix /api/auth)
- [x] T023 [US1] Implement POST /api/auth/signup endpoint in backend/src/routes/auth.py (validate request, call AuthService.create_user, generate JWT, set httpOnly cookie, return 201 with user)
- [x] T024 [US1] Implement POST /api/auth/signin endpoint in backend/src/routes/auth.py (validate request, call AuthService.verify_password, generate JWT, set httpOnly cookie, return 200 with user)
- [x] T025 [US1] Implement POST /api/auth/signout endpoint in backend/src/routes/auth.py (clear JWT cookie with Max-Age=0, return 200 with success message)
- [x] T026 [US1] Implement GET /api/auth/me endpoint in backend/src/routes/auth.py (use verify_jwt dependency, lookup user by authenticated user_id, return 200 with user or 401)
- [x] T027 [US1] Register auth router in backend/src/main.py (app.include_router)
- [x] T028 [US1] Add input validation and error handling for US1 endpoints (HTTPException for 400/401/409, Pydantic validation for request body, clear error messages)

**Checkpoint**: ✅ Run US1 tests - all should PASS (green phase). User Story 1 is fully functional and independently testable.

---

## Phase 4: User Story 2 - Secure Task Access with User Isolation (Priority: P2)

**Goal**: Authenticated users can only access their own tasks, ensuring complete data isolation

**Independent Test**: Create two user accounts (Alice, Bob). Alice creates a task. Bob attempts to access Alice's task by ID. Verify Bob receives 403 Forbidden. Verify Alice can only see her own tasks in the list.

**Acceptance Criteria** (from spec.md):
- Authenticated user can only see their own tasks in task list
- Attempting to access another user's task returns 403 Forbidden
- Creating a task associates it with authenticated user
- Updating/deleting a task verifies ownership before allowing operation
- All task endpoints require valid JWT token (401 if missing/invalid)

### Tests for User Story 2 (TDD - Write First, Ensure FAIL)

- [x] T029 [P] [US2] Write contract test for secured task endpoints in backend/tests/contract/test_task_api.py (test_list_tasks_requires_auth → 401 without token, test_list_tasks_with_auth → 200, test_list_tasks_user_isolation → Alice cannot see Bob's tasks)
- [x] T030 [P] [US2] Write contract test for task ownership in backend/tests/contract/test_task_api.py (test_get_task_wrong_user → 403, test_update_task_wrong_user → 403, test_delete_task_wrong_user → 403, test_complete_task_wrong_user → 403)
- [x] T031 [P] [US2] Write integration test for User Story 2 in backend/tests/integration/test_user_isolation.py (test_user_story_2_data_isolation: Alice creates task, Bob creates task, verify each user only sees their own tasks, verify cross-user access returns 403)

**Checkpoint**: ✅ All US2 tests written and FAILING (red phase) - COMPLETE

### Implementation for User Story 2

- [x] T032 [US2] Update GET /api/{user_id}/tasks endpoint in backend/src/routes/tasks.py (add user_id: str = Depends(verify_jwt), verify URL user_id matches authenticated user_id, raise 403 if mismatch, pass authenticated user_id to service)
- [x] T033 [US2] Update POST /api/{user_id}/tasks endpoint in backend/src/routes/tasks.py (add JWT dependency, verify user_id match, ensure created task has authenticated user_id)
- [x] T034 [US2] Update GET /api/{user_id}/tasks/{id} endpoint in backend/src/routes/tasks.py (add JWT dependency, verify user_id match, service filters by user_id)
- [x] T035 [US2] Update PUT /api/{user_id}/tasks/{id} endpoint in backend/src/routes/tasks.py (add JWT dependency, verify user_id match, service verifies ownership)
- [x] T036 [US2] Update DELETE /api/{user_id}/tasks/{id} endpoint in backend/src/routes/tasks.py (add JWT dependency, verify user_id match, service verifies ownership)
- [x] T037 [US2] Update PATCH /api/{user_id}/tasks/{id}/complete endpoint in backend/src/routes/tasks.py (add JWT dependency, verify user_id match, service verifies ownership)
- [x] T038 [US2] Update TaskService methods in backend/src/services/task_service.py to enforce user_id filtering (all queries MUST include WHERE user_id = authenticated_user_id - already implemented correctly)
- [x] T039 [US2] Add ownership verification helper in backend/src/routes/tasks.py (verify_user_match function: compare URL user_id with authenticated user_id, raise 403 if mismatch)

**Checkpoint**: ✅ Run US2 tests - all should PASS (green phase). User Stories 1 AND 2 are both independently functional. - COMPLETE

---

## Phase 5: User Story 3 - Persistent and Secure Sessions (Priority: P3)

**Goal**: Users remain authenticated across page navigations and browser sessions (within 24h validity period)

**Independent Test**: Sign in to the application, navigate between pages, close browser, reopen browser within 24 hours. Verify user is still authenticated. Test that expired or invalid tokens trigger re-authentication.

**Acceptance Criteria** (from spec.md):
- User remains authenticated across page navigations without re-signin
- User remains authenticated after closing and reopening browser (within 24h)
- Expired session redirects to sign-in page with clear message
- Invalid or tampered token is rejected and user prompted to sign in

### Tests for User Story 3 (TDD - Write First, Ensure FAIL)

- [ ] T040 [P] [US3] Write frontend component test for auth persistence in frontend/src/lib/auth.test.ts (test_session_restored_on_page_load, test_expired_token_clears_session, test_invalid_token_redirects_to_signin)
- [ ] T041 [P] [US3] Write frontend integration test in frontend/src/app/(auth)/signin/page.test.tsx (test_successful_signin_redirects_to_dashboard, test_failed_signin_shows_error)

**Checkpoint**: ✅ All US3 tests written and FAILING (red phase)

### Implementation for User Story 3

- [ ] T042 [US3] Configure Better Auth in frontend/src/lib/auth.ts (initialize with JWT strategy, httpOnly cookies, 24h expiration, BETTER_AUTH_SECRET from env)
- [ ] T043 [US3] Create SignUpForm component in frontend/src/components/auth/SignUpForm.tsx (form with email, password, name fields, validation, error display, call signup API)
- [ ] T044 [US3] Create SignInForm component in frontend/src/components/auth/SignInForm.tsx (form with email, password fields, validation, error display, call signin API)
- [ ] T045 [US3] Create signup page in frontend/src/app/(auth)/signup/page.tsx (render SignUpForm, redirect to dashboard on success)
- [ ] T046 [US3] Create signin page in frontend/src/app/(auth)/signin/page.tsx (render SignInForm, redirect to dashboard on success)
- [ ] T047 [US3] Update API client in frontend/src/lib/api.ts (configure to include credentials in requests, handle 401 by redirecting to signin, handle 403 with permission error)
- [ ] T048 [US3] Create route protection middleware in frontend/src/middleware.ts (check for valid JWT token, redirect unauthenticated users to signin, allow public access to auth pages)
- [ ] T049 [US3] Update root layout in frontend/src/app/layout.tsx (wrap app with Better Auth provider, add auth context for components)
- [ ] T050 [US3] Update dashboard page in frontend/src/app/dashboard/page.tsx (add auth check, display current user info, add sign out button, show loading state while checking session)
- [ ] T051 [US3] Implement session restoration logic in frontend/src/lib/auth.ts (check for valid token on app load, restore user session if token valid, clear session if token expired)
- [ ] T052 [US3] Add token expiration handling in frontend/src/lib/api.ts (detect 401 responses, clear local session, redirect to signin with "Session expired" message)

**Checkpoint**: ✅ Run US3 tests - all should PASS (green phase). All user stories (US1, US2, US3) are now independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final validation

- [x] T053 [P] Add structured logging to auth endpoints in backend/src/routes/auth.py (log signup attempts, signin attempts, user_id, operation type, success/failure)
- [x] T054 [P] Add structured logging to secured task endpoints in backend/src/routes/tasks.py (log authenticated user_id, task_id, operation type)
- [x] T055 [P] Create unit tests for JWT middleware in backend/tests/unit/test_jwt_middleware.py (test_verify_jwt_valid_token, test_verify_jwt_expired_token → 401, test_verify_jwt_invalid_signature → 401, test_verify_jwt_missing_token → 401)
- [x] T056 [P] Create unit tests for AuthService in backend/tests/unit/test_auth_service.py (test_create_user_hashes_password, test_verify_password_correct, test_verify_password_incorrect, test_generate_jwt_payload)
- [x] T057 Add API documentation examples to backend/src/routes/auth.py (FastAPI response_model, example values, descriptions per contracts/auth-api.yaml)
- [x] T058 Update backend/README.md with authentication setup instructions (environment variables, database migration, JWT secret generation)
- [x] T059 Create frontend README.md with Better Auth setup instructions (environment variables, CORS configuration, cookie settings)
- [ ] T060 Run full test suite with coverage report (pytest --cov=src --cov-report=html, verify >80% coverage for auth modules)
- [ ] T061 Validate quickstart.md instructions (follow all steps, test all curl examples, verify expected responses)
- [ ] T062 Security audit: verify password hashing, JWT signature, user isolation, no secrets in logs
- [ ] T063 Performance testing: verify signin <2s, token verification <50ms, 100 concurrent auth requests handled

**Note**: T060, T061, T063 require manual execution after deployment setup with actual Neon database connection.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User Story 1 (P1): Can start after Foundational - No dependencies on other stories
  - User Story 2 (P2): Can start after Foundational - Depends on US1 for auth infrastructure but independently testable
  - User Story 3 (P3): Can start after Foundational - Depends on US1 for backend auth but independently testable
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Independent - Can start after Foundational (Phase 2)
- **User Story 2 (P2)**: Depends on US1 auth infrastructure - Secures existing task endpoints with JWT
- **User Story 3 (P3)**: Depends on US1 backend auth - Implements frontend UI and session management

### Within Each User Story

1. **Tests FIRST** (TDD red phase): Write all tests, ensure they FAIL
2. **Implementation** (TDD green phase): Implement to make tests pass
3. **Refactor** (TDD refactor phase): Clean up code while keeping tests green
4. **Checkpoint**: Verify story works independently before moving to next

### Parallel Opportunities

**Phase 1 (Setup)**:
- T002, T003, T004, T005 can run in parallel (different files)

**Phase 2 (Foundational)**:
- T007 (schemas) and T012 (test fixtures) can run in parallel with other tasks
- T006-T011 should be mostly sequential (models → config → middleware)

**Phase 3 (User Story 1)**:
- T014, T015, T016, T017, T018 (all tests) can run in parallel
- T019, T020, T021 (service methods) can run in parallel

**Phase 4 (User Story 2)**:
- T029, T030, T031 (all tests) can run in parallel
- T032-T037 (route updates) can run carefully in parallel (same file, coordinate edits)

**Phase 5 (User Story 3)**:
- T040, T041 (tests) can run in parallel
- T043, T044 (form components) can run in parallel
- T045, T046 (auth pages) can run in parallel

**Phase 6 (Polish)**:
- T053, T054, T055, T056, T058, T059 can run in parallel (different files)

**Cross-Story Parallelism**:
- Once Foundational (Phase 2) is complete, User Stories 1 and 3 can be developed in parallel by different team members (backend and frontend)
- User Story 2 must wait for US1 to complete (depends on JWT middleware)

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (TDD red phase):
Task T014: "Write contract test for POST /api/auth/signup"
Task T015: "Write contract test for POST /api/auth/signin"
Task T016: "Write contract test for POST /api/auth/signout"
Task T017: "Write contract test for GET /api/auth/me"
Task T018: "Write integration test for User Story 1"

# After tests are written and failing, implement service methods in parallel:
Task T019: "Implement AuthService.create_user()"
Task T020: "Implement AuthService.verify_password()"
Task T021: "Implement AuthService.generate_jwt()"

# Then implement endpoints sequentially:
Task T022-T028: Implement routes and register router
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T005)
2. Complete Phase 2: Foundational (T006-T013) - CRITICAL BLOCKER
3. Complete Phase 3: User Story 1 (T014-T028)
   - Write tests first (T014-T018) - ensure FAIL
   - Implement (T019-T028) - make tests PASS
4. **STOP and VALIDATE**: Run all US1 tests independently
5. Deploy/demo MVP (users can sign up and sign in)

**MVP Scope**: 28 tasks total (T001-T028)

### Incremental Delivery

1. **Foundation** (T001-T013): Setup + Foundational → Backend auth infrastructure ready
2. **MVP** (T014-T028): Add User Story 1 → Test independently → Deploy/Demo (signup/signin working)
3. **Enhancement 1** (T029-T039): Add User Story 2 → Test independently → Deploy/Demo (task isolation enforced)
4. **Enhancement 2** (T040-T052): Add User Story 3 → Test independently → Deploy/Demo (frontend UI complete)
5. **Polish** (T053-T063): Cross-cutting improvements → Final deployment

Each increment adds value without breaking previous functionality.

### Parallel Team Strategy

With multiple developers:

1. **Together**: Complete Setup (Phase 1) + Foundational (Phase 2)
2. **Once Foundational is done**:
   - Developer A: User Story 1 backend (T014-T028)
   - Developer B: User Story 3 frontend (T040-T052) - can start in parallel with US1
3. **After US1 complete**:
   - Developer A: User Story 2 (T029-T039) - secures existing endpoints
4. **Together**: Polish phase (T053-T063)

---

## Task Summary

**Total Tasks**: 63 tasks

**Tasks by Phase**:
- Phase 1 (Setup): 5 tasks
- Phase 2 (Foundational): 8 tasks
- Phase 3 (User Story 1 - P1): 15 tasks (5 tests + 10 implementation)
- Phase 4 (User Story 2 - P2): 11 tasks (3 tests + 8 implementation)
- Phase 5 (User Story 3 - P3): 13 tasks (2 tests + 11 implementation)
- Phase 6 (Polish): 11 tasks

**Tasks by User Story**:
- User Story 1 (Registration and Sign-In): 15 tasks
- User Story 2 (User Isolation): 11 tasks
- User Story 3 (Session Persistence): 13 tasks
- Infrastructure (Setup + Foundational): 13 tasks
- Polish (Cross-cutting): 11 tasks

**Parallel Opportunities**: 23 tasks marked [P] can run in parallel within their phase

**Test Tasks**: 11 test tasks (contract + integration tests for all user stories)

**MVP Scope**: First 28 tasks (Setup + Foundational + User Story 1)

---

## Notes

- **[P] marker**: Tasks that can run in parallel (different files, no dependencies)
- **[Story] label**: Maps task to specific user story for traceability (US1, US2, US3)
- **TDD Cycle**: Write tests first (red) → Implement (green) → Refactor → Commit
- **Independent Stories**: Each user story can be tested and deployed independently
- **Checkpoints**: Stop after each user story to validate independently
- **File Paths**: All paths are exact and reference specific files per plan.md structure
- **Constitution Compliance**: All tasks follow Test-First Development (MANDATORY)
- **User Isolation**: All task endpoints enforce user data isolation (return 403 for cross-user access)
- **Error Handling**: Consistent HTTP status codes (400, 401, 403, 409) per contracts/auth-api.yaml
- **Security**: JWT tokens in httpOnly cookies, passwords hashed with bcrypt, shared secret in environment variables

---

**Generated**: 2026-02-08
**Feature**: Authentication & User Context
**Branch**: 002-auth-jwt
**Ready for**: `/sp.implement` command to execute tasks via Claude Code
