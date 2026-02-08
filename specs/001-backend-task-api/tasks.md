---
description: "Task breakdown for Backend Task API & Data Layer implementation"
---

# Tasks: Backend Task API & Data Layer

**Input**: Design documents from `/specs/001-backend-task-api/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Test tasks are included per constitution requirement (Test-First Development is MANDATORY)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app structure**: `backend/src/`, `backend/tests/`
- All paths are relative to repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create backend directory structure per plan.md (backend/src/, backend/tests/, backend/src/models/, backend/src/routes/, backend/src/services/, backend/src/schemas/, backend/src/middleware/)
- [x] T002 Initialize Python project with requirements.txt (fastapi, sqlmodel, psycopg2-binary, uvicorn, python-dotenv, pytest, pytest-asyncio, httpx, pytest-cov)
- [x] T003 [P] Create .env.example file in backend/ with DATABASE_URL, ENVIRONMENT, LOG_LEVEL placeholders
- [x] T004 [P] Create backend/README.md with setup instructions from quickstart.md
- [x] T005 [P] Configure pytest in backend/pytest.ini with asyncio mode and coverage settings

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T006 Create database configuration in backend/src/config.py (load DATABASE_URL from environment, validate required settings)
- [x] T007 Create database connection and session management in backend/src/db.py (SQLModel engine with connection pooling: pool_size=5, max_overflow=10, pool_pre_ping=True, pool_recycle=3600)
- [x] T008 Create Task SQLModel entity in backend/src/models/task.py (id, user_id, title, description, completed, created_at, updated_at per data-model.md)
- [x] T009 [P] Create Pydantic request/response schemas in backend/src/schemas/task_schemas.py (TaskCreate, TaskUpdate, TaskResponse per contracts/schemas.json)
- [x] T010 Create FastAPI application in backend/src/main.py (app initialization, CORS middleware, health check endpoint)
- [x] T011 Create pytest fixtures in backend/tests/conftest.py (in-memory SQLite engine, test session, test client with dependency override)
- [x] T012 [P] Create base error handling middleware in backend/src/middleware/__init__.py (global exception handler for 500 errors)

**Checkpoint**: ✅ Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Create and View Tasks (Priority: P1) 🎯 MVP

**Goal**: Users can create new tasks and view their task list to track todos

**Independent Test**: Create a task via POST /api/{user_id}/tasks, then retrieve it via GET /api/{user_id}/tasks and GET /api/{user_id}/tasks/{id}. Verify user data isolation by attempting to access another user's tasks.

**Acceptance Criteria** (from spec.md):
- User can POST a new task with title and description → 201 response with task details
- User can GET all their tasks → 200 response with task array
- User can GET a specific task by ID → 200 response with task details
- User data isolation enforced (user A cannot see user B's tasks)

### Tests for User Story 1 (TDD - Write First, Ensure FAIL)

- [x] T013 [P] [US1] Write contract test for POST /api/{user_id}/tasks in backend/tests/contract/test_task_api.py (test_create_task: valid data → 201, test_create_task_empty_title → 400, test_create_task_title_too_long → 400)
- [x] T014 [P] [US1] Write contract test for GET /api/{user_id}/tasks in backend/tests/contract/test_task_api.py (test_list_tasks: returns array, test_list_tasks_empty: returns empty array, test_list_tasks_user_isolation: user A cannot see user B's tasks)
- [x] T015 [P] [US1] Write contract test for GET /api/{user_id}/tasks/{id} in backend/tests/contract/test_task_api.py (test_get_task: returns task, test_get_task_not_found → 404, test_get_task_wrong_user → 404)
- [x] T016 [P] [US1] Write integration test for User Story 1 in backend/tests/integration/test_user_stories.py (test_user_story_1_create_and_view: complete user journey from creation to viewing)

**Checkpoint**: ✅ All US1 tests written and FAILING (red phase)

### Implementation for User Story 1

- [x] T017 [US1] Implement TaskService.create_task() in backend/src/services/task_service.py (validate title length, create task with user_id, return task object)
- [x] T018 [US1] Implement TaskService.list_tasks() in backend/src/services/task_service.py (filter by user_id, order by created_at desc, return task list)
- [x] T019 [US1] Implement TaskService.get_task() in backend/src/services/task_service.py (filter by id AND user_id, return task or None)
- [x] T020 [US1] Create task router in backend/src/routes/tasks.py (initialize APIRouter with prefix /api/{user_id}/tasks)
- [x] T021 [US1] Implement POST /api/{user_id}/tasks endpoint in backend/src/routes/tasks.py (validate user_id path param, call TaskService.create_task, return 201 with task)
- [x] T022 [US1] Implement GET /api/{user_id}/tasks endpoint in backend/src/routes/tasks.py (call TaskService.list_tasks, return 200 with task array)
- [x] T023 [US1] Implement GET /api/{user_id}/tasks/{id} endpoint in backend/src/routes/tasks.py (call TaskService.get_task, return 200 or 404)
- [x] T024 [US1] Register task router in backend/src/main.py (app.include_router)
- [x] T025 [US1] Add input validation and error handling for US1 endpoints (HTTPException for 400/404, Pydantic validation for request body)

**Checkpoint**: ✅ Run US1 tests - all should PASS (green phase). User Story 1 is fully functional and independently testable.

---

## Phase 4: User Story 2 - Update and Delete Tasks (Priority: P2)

**Goal**: Users can update task details and delete tasks they no longer need to keep their task list accurate

**Independent Test**: Create a task (using US1), update its title/description via PUT /api/{user_id}/tasks/{id}, verify changes. Delete the task via DELETE /api/{user_id}/tasks/{id}, verify it's gone.

**Acceptance Criteria** (from spec.md):
- User can PUT to update task title/description → 200 response with updated task
- User can DELETE a task → 204 response (no content)
- Ownership validation: user cannot update/delete another user's task → 404
- Non-existent task returns 404

### Tests for User Story 2 (TDD - Write First, Ensure FAIL)

- [x] T026 [P] [US2] Write contract test for PUT /api/{user_id}/tasks/{id} in backend/tests/contract/test_task_api.py (test_update_task: valid data → 200, test_update_task_not_found → 404, test_update_task_wrong_user → 404, test_update_task_invalid_data → 400)
- [x] T027 [P] [US2] Write contract test for DELETE /api/{user_id}/tasks/{id} in backend/tests/contract/test_task_api.py (test_delete_task: → 204, test_delete_task_not_found → 404, test_delete_task_wrong_user → 404)
- [x] T028 [P] [US2] Write integration test for User Story 2 in backend/tests/integration/test_user_stories.py (test_user_story_2_update_and_delete: create task, update it, verify changes, delete it, verify gone)

**Checkpoint**: ✅ All US2 tests written and FAILING (red phase)

### Implementation for User Story 2

- [x] T029 [US2] Implement TaskService.update_task() in backend/src/services/task_service.py (find task by id AND user_id, update title/description, update updated_at, return updated task or None)
- [x] T030 [US2] Implement TaskService.delete_task() in backend/src/services/task_service.py (find task by id AND user_id, delete if found, return True/False)
- [x] T031 [US2] Implement PUT /api/{user_id}/tasks/{id} endpoint in backend/src/routes/tasks.py (call TaskService.update_task, return 200 with updated task or 404)
- [x] T032 [US2] Implement DELETE /api/{user_id}/tasks/{id} endpoint in backend/src/routes/tasks.py (call TaskService.delete_task, return 204 or 404)
- [x] T033 [US2] Add validation and error handling for US2 endpoints (ownership validation, 404 for non-existent tasks, 400 for invalid input)

**Checkpoint**: ✅ Run US2 tests - all should PASS (green phase). User Stories 1 AND 2 are both independently functional.

---

## Phase 5: User Story 3 - Mark Tasks Complete (Priority: P3)

**Goal**: Users can mark tasks as complete or incomplete to track their progress

**Independent Test**: Create a task (using US1), toggle its completion status via PATCH /api/{user_id}/tasks/{id}/complete, verify completed=true. Toggle again, verify completed=false.

**Acceptance Criteria** (from spec.md):
- User can PATCH to toggle completion status → 200 response with updated task
- Toggle behavior: incomplete → complete, complete → incomplete
- Ownership validation: user cannot complete another user's task → 404

### Tests for User Story 3 (TDD - Write First, Ensure FAIL)

- [x] T034 [P] [US3] Write contract test for PATCH /api/{user_id}/tasks/{id}/complete in backend/tests/contract/test_task_api.py (test_toggle_completion_incomplete_to_complete: → 200 with completed=true, test_toggle_completion_complete_to_incomplete: → 200 with completed=false, test_toggle_completion_not_found → 404, test_toggle_completion_wrong_user → 404)
- [x] T035 [P] [US3] Write integration test for User Story 3 in backend/tests/integration/test_user_stories.py (test_user_story_3_mark_complete: create task, toggle to complete, verify status, toggle back to incomplete, verify status)

**Checkpoint**: ✅ All US3 tests written and FAILING (red phase)

### Implementation for User Story 3

- [x] T036 [US3] Implement TaskService.toggle_completion() in backend/src/services/task_service.py (find task by id AND user_id, toggle completed field, update updated_at, return updated task or None)
- [x] T037 [US3] Implement PATCH /api/{user_id}/tasks/{id}/complete endpoint in backend/src/routes/tasks.py (call TaskService.toggle_completion, return 200 with updated task or 404)
- [x] T038 [US3] Add validation and error handling for US3 endpoint (ownership validation, 404 for non-existent tasks)

**Checkpoint**: ✅ Run US3 tests - all should PASS (green phase). All user stories (US1, US2, US3) are now independently functional.
- User can PUT to update task title/description → 200 response with updated task
- User can DELETE a task → 204 response (no content)
- Ownership validation: user cannot update/delete another user's task → 404
- Non-existent task returns 404

### Tests for User Story 2 (TDD - Write First, Ensure FAIL)

- [ ] T026 [P] [US2] Write contract test for PUT /api/{user_id}/tasks/{id} in backend/tests/contract/test_task_api.py (test_update_task: valid data → 200, test_update_task_not_found → 404, test_update_task_wrong_user → 404, test_update_task_invalid_data → 400)
- [ ] T027 [P] [US2] Write contract test for DELETE /api/{user_id}/tasks/{id} in backend/tests/contract/test_task_api.py (test_delete_task: → 204, test_delete_task_not_found → 404, test_delete_task_wrong_user → 404)
- [ ] T028 [P] [US2] Write integration test for User Story 2 in backend/tests/integration/test_user_stories.py (test_user_story_2_update_and_delete: create task, update it, verify changes, delete it, verify gone)

**Checkpoint**: All US2 tests written and FAILING (red phase)

### Implementation for User Story 2

- [ ] T029 [US2] Implement TaskService.update_task() in backend/src/services/task_service.py (find task by id AND user_id, update title/description, update updated_at, return updated task or None)
- [ ] T030 [US2] Implement TaskService.delete_task() in backend/src/services/task_service.py (find task by id AND user_id, delete if found, return True/False)
- [ ] T031 [US2] Implement PUT /api/{user_id}/tasks/{id} endpoint in backend/src/routes/tasks.py (call TaskService.update_task, return 200 with updated task or 404)
- [ ] T032 [US2] Implement DELETE /api/{user_id}/tasks/{id} endpoint in backend/src/routes/tasks.py (call TaskService.delete_task, return 204 or 404)
- [ ] T033 [US2] Add validation and error handling for US2 endpoints (ownership validation, 404 for non-existent tasks, 400 for invalid input)

**Checkpoint**: Run US2 tests - all should PASS (green phase). User Stories 1 AND 2 are both independently functional.

---

## Phase 5: User Story 3 - Mark Tasks Complete (Priority: P3)

**Goal**: Users can mark tasks as complete or incomplete to track their progress

**Independent Test**: Create a task (using US1), toggle its completion status via PATCH /api/{user_id}/tasks/{id}/complete, verify completed=true. Toggle again, verify completed=false.

**Acceptance Criteria** (from spec.md):
- User can PATCH to toggle completion status → 200 response with updated task
- Toggle behavior: incomplete → complete, complete → incomplete
- Ownership validation: user cannot complete another user's task → 404

### Tests for User Story 3 (TDD - Write First, Ensure FAIL)

- [ ] T034 [P] [US3] Write contract test for PATCH /api/{user_id}/tasks/{id}/complete in backend/tests/contract/test_task_api.py (test_toggle_completion_incomplete_to_complete: → 200 with completed=true, test_toggle_completion_complete_to_incomplete: → 200 with completed=false, test_toggle_completion_not_found → 404, test_toggle_completion_wrong_user → 404)
- [ ] T035 [P] [US3] Write integration test for User Story 3 in backend/tests/integration/test_user_stories.py (test_user_story_3_mark_complete: create task, toggle to complete, verify status, toggle back to incomplete, verify status)

**Checkpoint**: All US3 tests written and FAILING (red phase)

### Implementation for User Story 3

- [ ] T036 [US3] Implement TaskService.toggle_completion() in backend/src/services/task_service.py (find task by id AND user_id, toggle completed field, update updated_at, return updated task or None)
- [ ] T037 [US3] Implement PATCH /api/{user_id}/tasks/{id}/complete endpoint in backend/src/routes/tasks.py (call TaskService.toggle_completion, return 200 with updated task or 404)
- [ ] T038 [US3] Add validation and error handling for US3 endpoint (ownership validation, 404 for non-existent tasks)

**Checkpoint**: Run US3 tests - all should PASS (green phase). All user stories (US1, US2, US3) are now independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final validation

- [x] T039 [P] Add structured logging to all endpoints in backend/src/routes/tasks.py (log request details, user_id, task_id, operation type)
- [x] T040 [P] Add database query logging in backend/src/db.py for debugging (log slow queries, connection pool stats)
- [x] T041 [P] Create unit tests for TaskService methods in backend/tests/unit/test_task_service.py (test business logic in isolation from database)
- [x] T042 Refactor common validation logic into shared validators in backend/src/schemas/task_schemas.py (title_not_empty validator, trim whitespace)
- [x] T043 Add API documentation examples to backend/src/routes/tasks.py (FastAPI response_model, example values, descriptions)
- [ ] T044 Run full test suite with coverage report (pytest --cov=src --cov-report=html, verify >80% coverage)
- [ ] T045 Validate quickstart.md instructions (follow setup steps, test all curl examples, verify expected responses)
- [x] T046 [P] Update backend/README.md with deployment instructions (environment variables, database setup, running in production)
- [ ] T047 Performance testing: verify <500ms response time for all endpoints with 100 tasks (load testing with locust or similar)

**Note**: T044, T045, T047 require manual execution after deployment setup with actual Neon database connection.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User Story 1 (P1): Can start after Foundational - No dependencies on other stories
  - User Story 2 (P2): Can start after Foundational - Uses US1 for testing but independently testable
  - User Story 3 (P3): Can start after Foundational - Uses US1 for testing but independently testable
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Independent - Can start after Foundational (Phase 2)
- **User Story 2 (P2)**: Independent - Can start after Foundational (Phase 2) - May use US1 endpoints for test setup but delivers independent value
- **User Story 3 (P3)**: Independent - Can start after Foundational (Phase 2) - May use US1 endpoints for test setup but delivers independent value

### Within Each User Story

1. **Tests FIRST** (TDD red phase): Write all tests, ensure they FAIL
2. **Implementation** (TDD green phase): Implement to make tests pass
3. **Refactor** (TDD refactor phase): Clean up code while keeping tests green
4. **Checkpoint**: Verify story works independently before moving to next

### Parallel Opportunities

**Phase 1 (Setup)**:
- T003, T004, T005 can run in parallel (different files)

**Phase 2 (Foundational)**:
- T009 (schemas) and T012 (middleware) can run in parallel with other tasks
- T006-T008 must be sequential (config → db → models)

**Phase 3 (User Story 1)**:
- T013, T014, T015, T016 (all tests) can run in parallel
- T017, T018, T019 (service methods) can run sequentially or carefully in parallel

**Phase 4 (User Story 2)**:
- T026, T027, T028 (all tests) can run in parallel

**Phase 5 (User Story 3)**:
- T034, T035 (all tests) can run in parallel

**Phase 6 (Polish)**:
- T039, T040, T041, T046 can run in parallel (different files)

**Cross-Story Parallelism**:
- Once Foundational (Phase 2) is complete, User Stories 1, 2, and 3 can be developed in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together (TDD red phase):
Task T013: "Write contract test for POST /api/{user_id}/tasks"
Task T014: "Write contract test for GET /api/{user_id}/tasks"
Task T015: "Write contract test for GET /api/{user_id}/tasks/{id}"
Task T016: "Write integration test for User Story 1"

# After tests are written and failing, implement service methods:
Task T017: "Implement TaskService.create_task()"
Task T018: "Implement TaskService.list_tasks()"
Task T019: "Implement TaskService.get_task()"

# Then implement endpoints sequentially:
Task T020-T025: Implement routes and register router
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T005)
2. Complete Phase 2: Foundational (T006-T012) - CRITICAL BLOCKER
3. Complete Phase 3: User Story 1 (T013-T025)
   - Write tests first (T013-T016) - ensure FAIL
   - Implement (T017-T025) - make tests PASS
4. **STOP and VALIDATE**: Run all US1 tests independently
5. Deploy/demo MVP (create and view tasks functionality)

**MVP Scope**: 47 tasks total (T001-T025 + foundational tasks)

### Incremental Delivery

1. **Foundation** (T001-T012): Setup + Foundational → Backend structure ready
2. **MVP** (T013-T025): Add User Story 1 → Test independently → Deploy/Demo
3. **Enhancement 1** (T026-T033): Add User Story 2 → Test independently → Deploy/Demo
4. **Enhancement 2** (T034-T038): Add User Story 3 → Test independently → Deploy/Demo
5. **Polish** (T039-T047): Cross-cutting improvements → Final deployment

Each increment adds value without breaking previous functionality.

### Parallel Team Strategy

With multiple developers:

1. **Together**: Complete Setup (Phase 1) + Foundational (Phase 2)
2. **Once Foundational is done**:
   - Developer A: User Story 1 (T013-T025)
   - Developer B: User Story 2 (T026-T033)
   - Developer C: User Story 3 (T034-T038)
3. **Merge and integrate**: Each story works independently
4. **Together**: Polish phase (T039-T047)

---

## Task Summary

**Total Tasks**: 47 tasks

**Tasks by Phase**:
- Phase 1 (Setup): 5 tasks
- Phase 2 (Foundational): 7 tasks
- Phase 3 (User Story 1 - P1): 13 tasks (4 tests + 9 implementation)
- Phase 4 (User Story 2 - P2): 8 tasks (3 tests + 5 implementation)
- Phase 5 (User Story 3 - P3): 5 tasks (2 tests + 3 implementation)
- Phase 6 (Polish): 9 tasks

**Tasks by User Story**:
- User Story 1 (Create and View): 13 tasks
- User Story 2 (Update and Delete): 8 tasks
- User Story 3 (Mark Complete): 5 tasks
- Infrastructure (Setup + Foundational): 12 tasks
- Polish (Cross-cutting): 9 tasks

**Parallel Opportunities**: 18 tasks marked [P] can run in parallel within their phase

**Test Tasks**: 9 test tasks (contract + integration tests for all user stories)

**MVP Scope**: First 25 tasks (Setup + Foundational + User Story 1)

---

## Notes

- **[P] marker**: Tasks that can run in parallel (different files, no dependencies)
- **[Story] label**: Maps task to specific user story for traceability (US1, US2, US3)
- **TDD Cycle**: Write tests first (red) → Implement (green) → Refactor → Commit
- **Independent Stories**: Each user story can be tested and deployed independently
- **Checkpoints**: Stop after each user story to validate independently
- **File Paths**: All paths are exact and reference specific files per plan.md structure
- **Constitution Compliance**: All tasks follow Test-First Development (MANDATORY)
- **Ownership Validation**: All endpoints enforce user data isolation (return 404 for cross-user access)
- **Error Handling**: Consistent HTTP status codes (400, 404, 500) per contracts/openapi.yaml

---

**Generated**: 2026-02-08
**Feature**: Backend Task API & Data Layer
**Branch**: 001-backend-task-api
**Ready for**: `/sp.implement` command to execute tasks via Claude Code
