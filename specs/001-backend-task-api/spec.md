# Feature Specification: Backend Task API & Data Layer

**Feature Branch**: `001-backend-task-api`
**Created**: 2026-02-08
**Status**: Draft
**Input**: User description: "Backend Task API & Data Layer for Todo Web Application - Secure, multi-user task management with persistent storage using Neon Serverless PostgreSQL. Strict enforcement of task ownership at API and database level."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create and View Tasks (Priority: P1)

As a user, I want to create new tasks and view my task list so that I can track my todos.

**Why this priority**: This is the core value proposition - users must be able to create and see their tasks. Without this, the application has no purpose. This story alone delivers a viable MVP.

**Independent Test**: Can be fully tested by making POST requests to create tasks and GET requests to retrieve them. Delivers immediate value by allowing users to store and retrieve their tasks.

**Acceptance Scenarios**:

1. **Given** a user with ID "user123", **When** they POST a new task with title "Buy groceries" and description "Milk, eggs, bread", **Then** the system creates the task, assigns it to user123, returns HTTP 201 with the task details including a unique task ID
2. **Given** user123 has created 3 tasks, **When** they GET /api/user123/tasks, **Then** the system returns HTTP 200 with all 3 tasks in the response body
3. **Given** user123 has tasks and user456 has tasks, **When** user123 requests GET /api/user123/tasks, **Then** the system returns only user123's tasks, not user456's tasks
4. **Given** a user with ID "user123", **When** they GET a specific task by ID that belongs to them, **Then** the system returns HTTP 200 with the complete task details

---

### User Story 2 - Update and Delete Tasks (Priority: P2)

As a user, I want to update task details and delete tasks I no longer need so that I can keep my task list accurate and relevant.

**Why this priority**: Once users can create and view tasks, they need to maintain them. This is essential for practical use but builds on P1 functionality.

**Independent Test**: Can be tested by creating a task (using P1 functionality), then updating its title/description and deleting it. Delivers value by allowing task maintenance.

**Acceptance Scenarios**:

1. **Given** user123 has a task with ID 5, **When** they PUT /api/user123/tasks/5 with updated title "Buy groceries and supplies", **Then** the system updates the task and returns HTTP 200 with the updated task details
2. **Given** user123 has a task with ID 5, **When** they DELETE /api/user123/tasks/5, **Then** the system removes the task and returns HTTP 204 (No Content)
3. **Given** user123 tries to update a task that belongs to user456, **When** they PUT /api/user123/tasks/{user456_task_id}, **Then** the system returns HTTP 404 (Not Found) to prevent cross-user access
4. **Given** user123 tries to delete a task that doesn't exist, **When** they DELETE /api/user123/tasks/999, **Then** the system returns HTTP 404 (Not Found)

---

### User Story 3 - Mark Tasks Complete (Priority: P3)

As a user, I want to mark tasks as complete or incomplete so that I can track my progress.

**Why this priority**: Completion tracking is important for task management but the system is usable without it. Users can still create, view, update, and delete tasks.

**Independent Test**: Can be tested by creating a task (P1), then toggling its completion status. Delivers value by adding progress tracking.

**Acceptance Scenarios**:

1. **Given** user123 has an incomplete task with ID 5, **When** they PATCH /api/user123/tasks/5/complete, **Then** the system marks the task as complete and returns HTTP 200 with the updated task
2. **Given** user123 has a complete task with ID 5, **When** they PATCH /api/user123/tasks/5/complete, **Then** the system marks the task as incomplete (toggle behavior) and returns HTTP 200
3. **Given** user123 tries to complete a task belonging to user456, **When** they PATCH /api/user123/tasks/{user456_task_id}/complete, **Then** the system returns HTTP 404 (Not Found)

---

### Edge Cases

- What happens when a user tries to create a task with an empty title? System returns HTTP 400 (Bad Request) with error message "Title is required"
- What happens when a user tries to create a task with a title exceeding 200 characters? System returns HTTP 400 (Bad Request) with error message "Title must be 200 characters or less"
- What happens when a user tries to create a task with a description exceeding 1000 characters? System returns HTTP 400 (Bad Request) with error message "Description must be 1000 characters or less"
- What happens when a user requests a task that doesn't exist? System returns HTTP 404 (Not Found) with error message "Task not found"
- What happens when a user tries to access another user's task? System returns HTTP 404 (Not Found) to prevent information disclosure about other users' tasks
- What happens when the database connection fails? System returns HTTP 500 (Internal Server Error) with error message "Service temporarily unavailable"
- What happens when a user provides an invalid user_id format in the URL? System returns HTTP 400 (Bad Request) with error message "Invalid user ID format"

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST store tasks persistently in Neon Serverless PostgreSQL database
- **FR-002**: System MUST associate each task with exactly one user via user_id field
- **FR-003**: System MUST provide a REST API endpoint to create new tasks (POST /api/{user_id}/tasks)
- **FR-004**: System MUST provide a REST API endpoint to list all tasks for a user (GET /api/{user_id}/tasks)
- **FR-005**: System MUST provide a REST API endpoint to retrieve a specific task (GET /api/{user_id}/tasks/{id})
- **FR-006**: System MUST provide a REST API endpoint to update a task (PUT /api/{user_id}/tasks/{id})
- **FR-007**: System MUST provide a REST API endpoint to delete a task (DELETE /api/{user_id}/tasks/{id})
- **FR-008**: System MUST provide a REST API endpoint to toggle task completion (PATCH /api/{user_id}/tasks/{id}/complete)
- **FR-009**: System MUST enforce task ownership - users can only access their own tasks
- **FR-010**: System MUST filter all database queries by the authenticated user_id from the URL path
- **FR-011**: System MUST validate that task titles are not empty and do not exceed 200 characters
- **FR-012**: System MUST validate that task descriptions do not exceed 1000 characters
- **FR-013**: System MUST return HTTP 400 (Bad Request) for invalid input data
- **FR-014**: System MUST return HTTP 404 (Not Found) when a task doesn't exist or doesn't belong to the requesting user
- **FR-015**: System MUST return HTTP 500 (Internal Server Error) for server-side failures
- **FR-016**: System MUST return HTTP 201 (Created) when a task is successfully created
- **FR-017**: System MUST return HTTP 200 (OK) for successful read and update operations
- **FR-018**: System MUST return HTTP 204 (No Content) for successful delete operations
- **FR-019**: System MUST automatically set created_at timestamp when a task is created
- **FR-020**: System MUST automatically update updated_at timestamp when a task is modified
- **FR-021**: System MUST store task completion status as a boolean field (default: false)
- **FR-022**: System MUST generate unique task IDs automatically (auto-increment integer)
- **FR-023**: System MUST accept user_id as a string to support various authentication systems
- **FR-024**: System MUST return consistent JSON response format for all endpoints
- **FR-025**: System MUST handle database connection errors gracefully without exposing internal details

### Key Entities

- **Task**: Represents a todo item with the following attributes:
  - Unique identifier (task ID)
  - Owner identifier (user ID) - links task to specific user
  - Title (short description of the task, required, max 200 characters)
  - Description (detailed information about the task, optional, max 1000 characters)
  - Completion status (boolean indicating if task is done)
  - Creation timestamp (when the task was created)
  - Last update timestamp (when the task was last modified)

- **User**: Referenced by user_id but not managed by this backend (managed by authentication system in Spec 2)
  - User ID (string identifier from authentication system)
  - Relationship: One user can have many tasks

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can create a new task and retrieve it within 500 milliseconds
- **SC-002**: Users can view their complete task list with 100 tasks in under 500 milliseconds
- **SC-003**: System correctly isolates user data - 100% of API requests return only the requesting user's tasks
- **SC-004**: All task operations persist correctly - 100% of created/updated tasks are retrievable after server restart
- **SC-005**: System handles invalid input gracefully - 100% of malformed requests receive appropriate 4xx error codes with clear error messages
- **SC-006**: System enforces data validation - 0% of tasks with empty titles or oversized fields are stored in the database
- **SC-007**: API contract compliance - 100% of endpoints return the exact HTTP status codes and response formats defined in the specification
- **SC-008**: Backend can be tested independently without frontend - all functionality verifiable via API testing tools (curl, Postman, pytest)

### Assumptions

- User IDs are provided as strings in the URL path (e.g., /api/user123/tasks)
- User authentication and JWT verification will be added in a separate specification (Spec 2)
- For now, any user_id in the URL is accepted (no validation that the user exists)
- Task IDs are auto-incrementing integers starting from 1
- Database connection string will be provided via environment variable (DATABASE_URL)
- All timestamps are stored in UTC
- Task list endpoint returns tasks in descending order by creation date (newest first)
- Soft delete is not required - DELETE operations permanently remove tasks
- No pagination is required for the task list endpoint (will be added in future phases if needed)
- No search or filtering capabilities beyond user_id (will be added in Phase V)
- API responses use JSON format exclusively
- CORS configuration will be handled separately for frontend integration
