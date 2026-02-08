# Data Model: Backend Task API & Data Layer

**Feature**: Backend Task API & Data Layer
**Branch**: `001-backend-task-api`
**Date**: 2026-02-08
**Phase**: Phase 1 - Design & Contracts

## Overview

This document defines the complete data model for the Task entity, including fields, validation rules, indexes, relationships, and state transitions.

---

## Entity: Task

### Purpose
Represents a single todo item owned by a user. Tasks are the core entity of the todo application, storing user-created action items with completion tracking.

### Table Name
`tasks` (plural, lowercase)

### Schema Definition

```python
from datetime import datetime
from sqlmodel import Field, SQLModel

class Task(SQLModel, table=True):
    """
    Task entity representing a user's todo item.

    [From]: specs/001-backend-task-api/spec.md §Requirements FR-001 through FR-025
    """
    __tablename__ = "tasks"

    # Primary Key
    id: int | None = Field(
        default=None,
        primary_key=True,
        description="Unique task identifier (auto-increment)"
    )

    # Foreign Key (User Ownership)
    user_id: str = Field(
        index=True,
        max_length=255,
        description="Owner identifier from authentication system"
    )

    # Task Content
    title: str = Field(
        min_length=1,
        max_length=200,
        description="Short description of the task (required)"
    )

    description: str | None = Field(
        default=None,
        max_length=1000,
        description="Detailed information about the task (optional)"
    )

    # Task Status
    completed: bool = Field(
        default=False,
        description="Completion status (true = done, false = pending)"
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="UTC timestamp when task was created"
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow},
        description="UTC timestamp when task was last modified"
    )
```

---

## Field Specifications

### id (Primary Key)
- **Type**: Integer
- **Constraints**: Primary key, auto-increment, not null
- **Range**: 1 to 2,147,483,647 (PostgreSQL integer max)
- **Generation**: Automatic (database sequence)
- **Uniqueness**: Globally unique across all tasks
- **Indexing**: Automatic (primary key index)

### user_id (Foreign Key)
- **Type**: String (VARCHAR)
- **Constraints**: Not null, indexed, max 255 characters
- **Format**: Any non-empty string (UUID, email, username, OAuth ID)
- **Validation**: Min length 1, max length 255
- **Relationship**: References user in external authentication system
- **Indexing**: B-tree index for fast filtering
- **Purpose**: Enforces task ownership and data isolation

### title
- **Type**: String (VARCHAR)
- **Constraints**: Not null, min 1 char, max 200 chars
- **Validation**:
  - Required field (cannot be empty or whitespace-only)
  - Length: 1-200 characters
  - No format restrictions (allows any UTF-8 characters)
- **Examples**:
  - ✅ "Buy groceries"
  - ✅ "Complete project report by Friday"
  - ❌ "" (empty string - rejected)
  - ❌ "A" * 201 (too long - rejected)

### description
- **Type**: String (TEXT) or NULL
- **Constraints**: Nullable, max 1000 chars
- **Validation**:
  - Optional field (can be null or empty)
  - Max length: 1000 characters
  - No format restrictions
- **Examples**:
  - ✅ null (no description)
  - ✅ "" (empty description)
  - ✅ "Milk, eggs, bread, cheese, butter"
  - ❌ "A" * 1001 (too long - rejected)

### completed
- **Type**: Boolean
- **Constraints**: Not null, default false
- **Values**:
  - `false` (0) - Task is pending/incomplete
  - `true` (1) - Task is done/complete
- **Default**: false (new tasks are incomplete)
- **Toggle**: PATCH endpoint flips the value

### created_at
- **Type**: DateTime (TIMESTAMP)
- **Constraints**: Not null, UTC timezone
- **Generation**: Automatic on insert (Python `datetime.utcnow()`)
- **Format**: ISO 8601 (e.g., "2026-02-08T14:30:00Z")
- **Immutable**: Never changes after creation
- **Purpose**: Audit trail, sorting (newest first)

### updated_at
- **Type**: DateTime (TIMESTAMP)
- **Constraints**: Not null, UTC timezone
- **Generation**: Automatic on insert and update
- **Format**: ISO 8601 (e.g., "2026-02-08T14:30:00Z")
- **Update Trigger**: SQLAlchemy `onupdate` refreshes on any field change
- **Purpose**: Audit trail, change tracking

---

## Indexes

### Primary Index
```sql
CREATE UNIQUE INDEX tasks_pkey ON tasks (id);
```
- **Purpose**: Enforce uniqueness, fast lookups by ID
- **Type**: B-tree (default)
- **Automatic**: Created by primary key constraint

### User ID Index
```sql
CREATE INDEX idx_tasks_user_id ON tasks (user_id);
```
- **Purpose**: Fast filtering by user (most common query)
- **Type**: B-tree
- **Cardinality**: High (many unique users)
- **Query Pattern**: `WHERE user_id = 'user123'`

### Composite Index (Future Optimization)
```sql
CREATE INDEX idx_tasks_user_completed ON tasks (user_id, completed);
```
- **Purpose**: Fast filtering by user and completion status
- **Type**: B-tree
- **Query Pattern**: `WHERE user_id = 'user123' AND completed = false`
- **Note**: Not required for Phase II, can be added in Phase V

---

## Relationships

### Task → User (Many-to-One)
- **Relationship**: Each task belongs to exactly one user
- **Foreign Key**: `task.user_id` references `user.id` (external system)
- **Cardinality**: Many tasks to one user
- **Cascade**: Not enforced (user management is external)
- **Orphan Handling**: Tasks remain if user is deleted (external system responsibility)

**Note**: User entity is NOT managed by this backend. User authentication and management is handled by Better Auth (Spec 2). The `user_id` field is a logical foreign key only.

---

## Validation Rules

### Field-Level Validation (Pydantic)

```python
from pydantic import BaseModel, Field, validator

class TaskCreate(BaseModel):
    """Request schema for creating a task"""
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=1000)

    @validator('title')
    def title_not_empty(cls, v):
        if not v or v.strip() == "":
            raise ValueError("Title cannot be empty or whitespace-only")
        return v.strip()

class TaskUpdate(BaseModel):
    """Request schema for updating a task"""
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=1000)

    @validator('title')
    def title_not_empty(cls, v):
        if not v or v.strip() == "":
            raise ValueError("Title cannot be empty or whitespace-only")
        return v.strip()

class TaskResponse(BaseModel):
    """Response schema for task operations"""
    id: int
    user_id: str
    title: str
    description: str | None
    completed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Enable ORM mode
```

### Business Logic Validation

1. **Ownership Validation**:
   - All operations MUST verify task belongs to requesting user
   - Query: `WHERE id = {task_id} AND user_id = {user_id}`
   - Failure: Return 404 (not 403) to prevent information disclosure

2. **Existence Validation**:
   - All operations on specific tasks MUST verify task exists
   - Query: `SELECT * FROM tasks WHERE id = {task_id} AND user_id = {user_id}`
   - Failure: Return 404 Not Found

3. **Input Sanitization**:
   - Title and description are trimmed (leading/trailing whitespace removed)
   - No HTML/script injection prevention needed (frontend responsibility)
   - Database handles SQL injection via parameterized queries

---

## State Transitions

### Task Lifecycle

```
[CREATE] → Incomplete (completed = false)
    ↓
[UPDATE] → Incomplete (completed unchanged)
    ↓
[TOGGLE] → Complete (completed = true)
    ↓
[TOGGLE] → Incomplete (completed = false)
    ↓
[DELETE] → Removed (permanent deletion)
```

### State Diagram

```
┌─────────────┐
│   Created   │ (completed = false)
└──────┬──────┘
       │
       ↓
┌─────────────┐
│ Incomplete  │ ←──────┐
└──────┬──────┘        │
       │               │
       │ PATCH         │ PATCH
       │ /complete     │ /complete
       ↓               │
┌─────────────┐        │
│  Complete   │ ───────┘
└──────┬──────┘
       │
       │ DELETE
       ↓
┌─────────────┐
│   Deleted   │ (permanent)
└─────────────┘
```

### Allowed Transitions

| From State | Action | To State | Endpoint |
|------------|--------|----------|----------|
| N/A | Create | Incomplete | POST /api/{user_id}/tasks |
| Incomplete | Update | Incomplete | PUT /api/{user_id}/tasks/{id} |
| Complete | Update | Complete | PUT /api/{user_id}/tasks/{id} |
| Incomplete | Toggle | Complete | PATCH /api/{user_id}/tasks/{id}/complete |
| Complete | Toggle | Incomplete | PATCH /api/{user_id}/tasks/{id}/complete |
| Any | Delete | Deleted | DELETE /api/{user_id}/tasks/{id} |

**Note**: Update (PUT) does NOT change completion status. Only PATCH /complete toggles the status.

---

## Database Migration

### Initial Schema Creation

```python
# backend/src/db.py
from sqlmodel import SQLModel, create_engine

def init_db():
    """Create all tables in the database"""
    SQLModel.metadata.create_all(engine)
```

### Migration Strategy

**Phase II**: Use `SQLModel.metadata.create_all()` for initial setup
- Simple, no migration history needed
- Suitable for development and initial deployment

**Future Phases**: Consider Alembic for schema migrations
- Track schema changes over time
- Support rollback and forward migrations
- Required when schema evolves (Phase III+)

---

## Query Patterns

### Common Queries

**List all tasks for a user** (GET /api/{user_id}/tasks):
```python
statement = select(Task).where(Task.user_id == user_id).order_by(Task.created_at.desc())
tasks = session.exec(statement).all()
```

**Get specific task** (GET /api/{user_id}/tasks/{id}):
```python
statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
task = session.exec(statement).first()
```

**Create task** (POST /api/{user_id}/tasks):
```python
task = Task(user_id=user_id, title=title, description=description)
session.add(task)
session.commit()
session.refresh(task)
```

**Update task** (PUT /api/{user_id}/tasks/{id}):
```python
statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
task = session.exec(statement).first()
if task:
    task.title = new_title
    task.description = new_description
    session.add(task)
    session.commit()
    session.refresh(task)
```

**Toggle completion** (PATCH /api/{user_id}/tasks/{id}/complete):
```python
statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
task = session.exec(statement).first()
if task:
    task.completed = not task.completed
    session.add(task)
    session.commit()
    session.refresh(task)
```

**Delete task** (DELETE /api/{user_id}/tasks/{id}):
```python
statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
task = session.exec(statement).first()
if task:
    session.delete(task)
    session.commit()
```

---

## Performance Considerations

### Index Usage
- **user_id index**: Used in all queries (100% hit rate)
- **Primary key index**: Used for specific task lookups
- **Query optimizer**: PostgreSQL automatically uses indexes

### Query Optimization
- **Limit results**: No pagination in Phase II, but queries are filtered by user_id (natural limit)
- **Avoid N+1**: Single query per operation (no joins needed)
- **Connection pooling**: Reuse database connections (see research.md)

### Scalability
- **Horizontal scaling**: Stateless backend, can add more instances
- **Database scaling**: Neon handles automatic scaling
- **Partitioning**: Not needed for Phase II (future consideration)

---

## Security Considerations

### Data Isolation
- **Enforcement**: All queries MUST include `WHERE user_id = {authenticated_user_id}`
- **Verification**: Contract tests verify cross-user access is blocked
- **Failure Mode**: Return 404 (not 403) to prevent user enumeration

### SQL Injection Prevention
- **Method**: SQLModel/SQLAlchemy uses parameterized queries
- **Validation**: Pydantic validates input types and formats
- **No raw SQL**: All queries use ORM (no string concatenation)

### Data Integrity
- **Constraints**: Database enforces NOT NULL, length limits
- **Validation**: Application validates before database insert
- **Timestamps**: Automatic, cannot be manipulated by users

---

## Testing Strategy

### Unit Tests (Model)
- Test field validation (min/max lengths)
- Test default values (completed = false)
- Test timestamp generation

### Integration Tests (Database)
- Test CRUD operations
- Test user data isolation
- Test query performance (<500ms)

### Contract Tests (API)
- Test all endpoints with valid/invalid data
- Test ownership enforcement
- Test error responses

---

## Summary

**Entity**: Task
**Table**: tasks
**Fields**: 7 (id, user_id, title, description, completed, created_at, updated_at)
**Indexes**: 2 (primary key, user_id)
**Relationships**: 1 (many-to-one with User)
**Validation**: Field-level (Pydantic) + Business logic (ownership)
**State Transitions**: 5 (create, update, toggle, delete)
**Query Patterns**: 6 (list, get, create, update, toggle, delete)

---

**Data Model Status**: ✅ COMPLETE
**Ready for Implementation**: Yes
**Next Step**: Create API contracts (OpenAPI specification)
