# Tasks: Frontend UI & Integration

**Input**: Design documents from `/specs/003-frontend-ui/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/api-client.ts, quickstart.md

**Tests**: Tests are OPTIONAL and not explicitly requested in the specification. This task list focuses on implementation only.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `frontend/src/` for source code
- All paths relative to repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Initialize Next.js 16+ project with TypeScript and App Router in frontend/ directory
- [ ] T002 Install core dependencies: next@^16.0.0, react@^18.0.0, typescript@^5.0.0, tailwindcss@^3.4.0
- [ ] T003 Install Better Auth dependencies: better-auth@^1.0.0, @better-auth/react@^1.0.0
- [ ] T004 Install form dependencies: react-hook-form@^7.50.0, zod@^3.22.0, @hookform/resolvers
- [ ] T005 [P] Configure Tailwind CSS in frontend/tailwind.config.js and frontend/src/app/globals.css
- [ ] T006 [P] Configure TypeScript in frontend/tsconfig.json with path aliases (@/*)
- [ ] T007 [P] Create .env.local with NEXT_PUBLIC_API_URL and BETTER_AUTH_SECRET
- [ ] T008 [P] Create .env.example template for environment variables
- [ ] T009 [P] Configure Next.js in frontend/next.config.js for API proxy and environment variables

**Checkpoint**: Project structure initialized, all dependencies installed, configuration complete

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T010 [P] Create TypeScript type definitions in frontend/src/types/user.ts (User, UserSession interfaces)
- [ ] T011 [P] Create TypeScript type definitions in frontend/src/types/task.ts (Task, TaskCreate, TaskUpdate interfaces)
- [ ] T012 Configure Better Auth in frontend/src/lib/auth.ts with JWT settings and httpOnly cookies
- [ ] T013 Create API client base implementation in frontend/src/lib/api.ts with fetch wrapper and error handling
- [ ] T014 Implement API client auth methods in frontend/src/lib/api.ts (signup, signin, signout, me)
- [ ] T015 Implement API client task methods in frontend/src/lib/api.ts (list, get, create, update, delete, toggleComplete)
- [ ] T016 [P] Create reusable Button component in frontend/src/components/ui/Button.tsx with Tailwind styles
- [ ] T017 [P] Create reusable Input component in frontend/src/components/ui/Input.tsx with validation support
- [ ] T018 [P] Create Spinner component in frontend/src/components/ui/Spinner.tsx for loading states
- [ ] T019 [P] Create ErrorMessage component in frontend/src/components/ui/ErrorMessage.tsx for error display
- [ ] T020 Create root layout in frontend/src/app/layout.tsx with Better Auth SessionProvider and global styles
- [ ] T021 [P] Create utility functions in frontend/src/lib/utils.ts for common operations (classNames, formatDate)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - User Authentication Flow (Priority: P1) 🎯 MVP

**Goal**: Users can sign up, sign in, and sign out through a web interface

**Independent Test**: Visit signup page, create account, sign out, sign back in. Verify authentication works end-to-end.

**Acceptance Criteria**:
- ✅ Signup page with email/password/name form (FR-001)
- ✅ Signin page with email/password form (FR-002)
- ✅ Form validation with clear error messages (FR-017)
- ✅ Automatic redirect to dashboard after signin (FR-003)
- ✅ Signout functionality clears session (FR-015)

### Implementation for User Story 1

- [ ] T022 [P] [US1] Create SignUpForm component in frontend/src/components/auth/SignUpForm.tsx with React Hook Form and Zod validation
- [ ] T023 [P] [US1] Create SignInForm component in frontend/src/components/auth/SignInForm.tsx with React Hook Form and Zod validation
- [ ] T024 [US1] Create signup page in frontend/src/app/(auth)/signup/page.tsx using SignUpForm component
- [ ] T025 [US1] Create signin page in frontend/src/app/(auth)/signin/page.tsx using SignInForm component
- [ ] T026 [US1] Create auth layout in frontend/src/app/(auth)/layout.tsx with centered card design
- [ ] T027 [US1] Implement signout functionality in root layout header with signout button
- [ ] T028 [US1] Add navigation links between signin and signup pages
- [ ] T029 [US1] Add loading states to auth forms during submission
- [ ] T030 [US1] Add error handling to auth forms with user-friendly messages

**Checkpoint**: At this point, User Story 1 should be fully functional - users can sign up, sign in, and sign out

---

## Phase 4: User Story 2 - Task Management Interface (Priority: P2)

**Goal**: Authenticated users can view, create, edit, delete, and complete tasks

**Independent Test**: Sign in, create multiple tasks, mark some complete, edit task details, delete tasks. Verify all CRUD operations work correctly.

**Acceptance Criteria**:
- ✅ Dashboard displays user's task list (FR-005)
- ✅ Create task form with title and description (FR-006)
- ✅ Mark tasks complete/incomplete with checkbox (FR-007)
- ✅ Edit task title and description (FR-008)
- ✅ Delete tasks with confirmation (FR-009)
- ✅ Empty state when no tasks exist (FR-013)
- ✅ Only user's own tasks visible (FR-018)

### Implementation for User Story 2

- [ ] T031 [P] [US2] Create TaskItem component in frontend/src/components/tasks/TaskItem.tsx with checkbox, edit, and delete buttons
- [ ] T032 [P] [US2] Create TaskList component in frontend/src/components/tasks/TaskList.tsx to render array of TaskItem components
- [ ] T033 [P] [US2] Create TaskForm component in frontend/src/components/tasks/TaskForm.tsx with React Hook Form and Zod validation
- [ ] T034 [P] [US2] Create EmptyState component in frontend/src/components/tasks/EmptyState.tsx with helpful message
- [ ] T035 [US2] Create dashboard page in frontend/src/app/dashboard/page.tsx with task list and create form
- [ ] T036 [US2] Implement task fetching on dashboard mount using API client
- [ ] T037 [US2] Implement task creation handler in dashboard page
- [ ] T038 [US2] Implement task update handler in dashboard page with inline editing or modal
- [ ] T039 [US2] Implement task deletion handler in dashboard page with confirmation dialog
- [ ] T040 [US2] Implement task completion toggle handler in dashboard page
- [ ] T041 [US2] Add optimistic UI updates for better perceived performance
- [ ] T042 [US2] Add loading states for task operations (creating, updating, deleting, toggling)
- [ ] T043 [US2] Add error handling for task operations with retry capability
- [ ] T044 [US2] Display empty state when user has no tasks

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - full task management functionality

---

## Phase 5: User Story 3 - Session Persistence and Error Handling (Priority: P3)

**Goal**: Session persists across page refreshes, loading states provide feedback, errors are user-friendly

**Independent Test**: Sign in, refresh browser, close and reopen tab, trigger errors. Verify session persists and error messages are clear.

**Acceptance Criteria**:
- ✅ Session persists across page refreshes (FR-014)
- ✅ Protected routes redirect unauthenticated users (FR-004)
- ✅ Authenticated users redirected from auth pages (FR-003)
- ✅ Loading indicators for operations >300ms (FR-011, SC-007)
- ✅ User-friendly error messages (FR-012, SC-006)
- ✅ Responsive design 320px+ (FR-016, SC-004)

### Implementation for User Story 3

- [ ] T045 [US3] Create middleware in frontend/src/middleware.ts for route protection
- [ ] T046 [US3] Configure middleware to redirect unauthenticated users from /dashboard to /signin
- [ ] T047 [US3] Configure middleware to redirect authenticated users from /signin and /signup to /dashboard
- [ ] T048 [US3] Add session expiration handling with redirect to signin and message
- [ ] T049 [P] [US3] Create TaskSkeleton component in frontend/src/components/tasks/TaskSkeleton.tsx for loading state
- [ ] T050 [US3] Add skeleton screens to dashboard during initial task fetch
- [ ] T051 [US3] Add loading spinners to buttons during async operations
- [ ] T052 [US3] Implement centralized error boundary for unexpected errors
- [ ] T053 [US3] Add network error detection with retry button
- [ ] T054 [US3] Add responsive design breakpoints for mobile (320px), tablet (768px), desktop (1024px+)
- [ ] T055 [US3] Test and fix layout on mobile devices (320px minimum width)
- [ ] T056 [US3] Add keyboard navigation support for all interactive elements
- [ ] T057 [US3] Add proper ARIA labels and semantic HTML for accessibility

**Checkpoint**: All user stories should now be independently functional with professional UX polish

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final deployment preparation

- [ ] T058 [P] Create landing page in frontend/src/app/page.tsx that redirects to signin or dashboard based on auth state
- [ ] T059 [P] Create 404 page in frontend/src/app/not-found.tsx with helpful message
- [ ] T060 [P] Add favicon and metadata in frontend/src/app/layout.tsx
- [ ] T061 [P] Create README.md in frontend/ directory with setup instructions
- [ ] T062 [P] Add ESLint configuration in frontend/.eslintrc.json for code quality
- [ ] T063 [P] Add Prettier configuration in frontend/.prettierrc for code formatting
- [ ] T064 Optimize bundle size by reviewing and removing unused dependencies
- [ ] T065 Add performance monitoring for page load times and API response times
- [ ] T066 Review and fix any console warnings or errors
- [ ] T067 Test full user journey: signup → signin → create task → complete task → delete task → signout
- [ ] T068 Verify all 18 functional requirements (FR-001 to FR-018) are implemented
- [ ] T069 Verify all 8 success criteria (SC-001 to SC-008) are met
- [ ] T070 Prepare for deployment: verify environment variables, build production bundle, test production build locally

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User Story 1 (P1): Can start after Foundational - No dependencies on other stories
  - User Story 2 (P2): Can start after Foundational - Requires US1 for authentication but independently testable
  - User Story 3 (P3): Can start after Foundational - Enhances US1 and US2 but independently testable
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Requires authentication from US1 but should be independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Enhances US1 and US2 with middleware, loading, and error handling

### Within Each User Story

- Components marked [P] can be built in parallel (different files)
- Page components depend on their child components being complete
- Event handlers depend on API client methods being implemented
- Loading and error states can be added after core functionality works

### Parallel Opportunities

**Phase 1 (Setup)**: Tasks T005-T009 can run in parallel (different config files)

**Phase 2 (Foundational)**:
- T010-T011 can run in parallel (different type files)
- T016-T019 can run in parallel (different UI components)
- T021 can run in parallel with other tasks

**Phase 3 (User Story 1)**:
- T022-T023 can run in parallel (different auth form components)
- T024-T025 can run in parallel after forms are complete (different pages)

**Phase 4 (User Story 2)**:
- T031-T034 can run in parallel (different task components)
- T041-T044 can be added in parallel after core functionality works

**Phase 5 (User Story 3)**:
- T049 can run in parallel with other tasks (skeleton component)
- T054-T057 can run in parallel (different polish tasks)

**Phase 6 (Polish)**:
- T058-T063 can run in parallel (different documentation and config files)

---

## Parallel Example: User Story 1

```bash
# Launch all auth form components together:
Task T022: "Create SignUpForm component in frontend/src/components/auth/SignUpForm.tsx"
Task T023: "Create SignInForm component in frontend/src/components/auth/SignInForm.tsx"

# Then launch both pages together:
Task T024: "Create signup page in frontend/src/app/(auth)/signup/page.tsx"
Task T025: "Create signin page in frontend/src/app/(auth)/signin/page.tsx"
```

## Parallel Example: User Story 2

```bash
# Launch all task components together:
Task T031: "Create TaskItem component in frontend/src/components/tasks/TaskItem.tsx"
Task T032: "Create TaskList component in frontend/src/components/tasks/TaskList.tsx"
Task T033: "Create TaskForm component in frontend/src/components/tasks/TaskForm.tsx"
Task T034: "Create EmptyState component in frontend/src/components/tasks/EmptyState.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T009)
2. Complete Phase 2: Foundational (T010-T021) - CRITICAL, blocks all stories
3. Complete Phase 3: User Story 1 (T022-T030)
4. **STOP and VALIDATE**: Test authentication flow independently
5. Deploy/demo if ready

**Deliverable**: Users can sign up, sign in, and sign out through a web interface

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo (Full task management!)
4. Add User Story 3 → Test independently → Deploy/Demo (Production-ready UX!)
5. Add Polish → Final deployment

Each story adds value without breaking previous stories.

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T021)
2. Once Foundational is done:
   - Developer A: User Story 1 (T022-T030)
   - Developer B: User Story 2 (T031-T044) - can start in parallel
   - Developer C: User Story 3 (T045-T057) - can start in parallel
3. Stories complete and integrate independently

---

## Agent Assignments

**All frontend tasks should be delegated to specialized agents:**

- **Phase 1-2 (Setup & Foundational)**: `nextjs-ui-architect` for project setup and base components
- **Phase 3 (User Story 1)**: `auth-security-specialist` for authentication implementation, `nextjs-ui-architect` for UI components
- **Phase 4 (User Story 2)**: `nextjs-ui-architect` for task management UI
- **Phase 5 (User Story 3)**: `auth-security-specialist` for middleware, `nextjs-ui-architect` for loading/error states
- **Phase 6 (Polish)**: `nextjs-ui-architect` for final polish and deployment prep

**NEVER implement frontend code directly - ALWAYS delegate to specialized agents via Task tool.**

---

## Notes

- [P] tasks = different files, no dependencies, can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Backend API already exists and is functional (Phase II: 002-auth-jwt)
- All API endpoints are documented in contracts/api-client.ts
- Follow quickstart.md for detailed implementation guidance per task

---

## Task Count Summary

- **Phase 1 (Setup)**: 9 tasks
- **Phase 2 (Foundational)**: 12 tasks (BLOCKING)
- **Phase 3 (User Story 1)**: 9 tasks
- **Phase 4 (User Story 2)**: 14 tasks
- **Phase 5 (User Story 3)**: 13 tasks
- **Phase 6 (Polish)**: 13 tasks

**Total**: 70 tasks

**Parallel Opportunities**: 23 tasks marked [P] can run in parallel within their phase

**MVP Scope**: Phases 1-3 (30 tasks) deliver authentication UI - minimum viable frontend

**Full Feature**: Phases 1-5 (57 tasks) deliver complete task management with professional UX

**Production Ready**: All phases (70 tasks) deliver deployment-ready application
