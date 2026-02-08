---
id: 003
title: Database Migration for Authentication Feature
stage: green
date: 2026-02-08
surface: agent
model: claude-sonnet-4-5
feature: 002-auth-jwt
branch: 002-auth-jwt
user: neon-db-architect
command: implement
labels: ["database", "migration", "authentication", "neon", "postgresql", "schema"]
links:
  spec: specs/002-auth-jwt/data-model.md
  ticket: null
  adr: null
  pr: null
files:
  - backend/migrations/README.md
  - backend/migrations/001_create_users_table.sql
  - backend/migrations/002_add_tasks_foreign_key.sql
  - backend/migrations/run_migrations.py
  - backend/migrations/create_test_user.py
  - backend/migrations/MIGRATION_SUMMARY.md
  - specs/002-auth-jwt/tasks.md
tests:
  - Migration 001: Create users table - PASSED
  - Migration 002: Add foreign key constraint - PASSED
  - Schema verification: users table - PASSED
  - Schema verification: foreign key constraint - PASSED
  - Index verification: all indexes created - PASSED
---

## Prompt

Create database migration for authentication feature (users table and foreign key constraint).

**Context**:
- Feature: 002-auth-jwt (Authentication & User Context)
- Database: Neon Serverless PostgreSQL
- Connection: Already configured in backend/.env (DATABASE_URL)
- Data Model: specs/002-auth-jwt/data-model.md

**Phase 2 Status**: Core authentication infrastructure complete (User model, JWT middleware, schemas)

**Your Tasks**:

**T009**: Create database migration script in backend/migrations/ to create users table
- Table name: `users`
- Columns:
  - id VARCHAR(255) PRIMARY KEY (UUID from Better Auth)
  - email VARCHAR(255) UNIQUE NOT NULL
  - password_hash VARCHAR(255) NOT NULL
  - name VARCHAR(255) NULL
  - created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
  - updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
- Indexes:
  - UNIQUE INDEX idx_users_email ON users(email)
  - INDEX idx_users_created_at ON users(created_at)
- Reference: specs/002-auth-jwt/data-model.md (lines 116-128)

**T010**: Add foreign key constraint from tasks.user_id to users.id
- Constraint: FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
- Verify tasks table has user_id column (should exist from Phase I)
- Add indexes if missing:
  - INDEX idx_tasks_user_id ON tasks(user_id)
  - INDEX idx_tasks_user_completed ON tasks(user_id, completed)
- Reference: specs/002-auth-jwt/data-model.md (lines 130-155)

**Requirements**:
- Create migration script in backend/migrations/ directory
- Use SQL format (not ORM migrations)
- Include rollback/down migration
- Test migration on Neon database
- Verify foreign key constraint works (cascade delete)
- Document migration in backend/migrations/README.md

**Existing Database**:
- tasks table already exists from Phase I (001-backend-task-api)
- Verify tasks.user_id column exists before adding foreign key
- If user_id column missing, add it first

**Mark completed tasks** in specs/002-auth-jwt/tasks.md by changing [ ] to [x]

## Response snapshot

Successfully created and executed database migrations for the authentication feature:

**Migration Files Created**:
1. `001_create_users_table.sql` - Creates users table with proper schema, indexes, and comments
2. `002_add_tasks_foreign_key.sql` - Adds foreign key constraint with cascade delete and composite indexes
3. `run_migrations.py` - Python script to run migrations with tracking, rollback support, and status checking
4. `create_test_user.py` - Helper script to create test user for existing tasks
5. `README.md` - Comprehensive migration documentation
6. `MIGRATION_SUMMARY.md` - Detailed summary of migration execution and verification

**Migration Execution**:
- Created schema_migrations tracking table
- Applied migration 001: users table created successfully
- Handled orphaned task issue by creating test user (user123)
- Applied migration 002: foreign key constraint added successfully
- All indexes created and verified

**Schema Verification**:
- Users table: 6 columns (id, email, password_hash, name, created_at, updated_at)
- Indexes: idx_users_email (unique), idx_users_created_at
- Foreign key: fk_tasks_user_id (tasks.user_id -> users.id ON DELETE CASCADE)
- Composite index: idx_tasks_user_completed (user_id, completed)

**Windows Compatibility**:
- Fixed Unicode encoding issues for Windows console
- Migration runner works correctly on Windows platform

**Tasks Completed**:
- [x] T009: Create users table migration
- [x] T010: Add foreign key constraint migration

## Outcome

- ✅ Impact: Database schema ready for authentication implementation. Users table created with proper indexes. Foreign key constraint enforces referential integrity between users and tasks. Cascade delete ensures data cleanup.
- 🧪 Tests: All migrations executed successfully on Neon database. Schema verification passed. Foreign key constraint verified. Index creation confirmed.
- 📁 Files: Created 6 files in backend/migrations/ directory. Updated specs/002-auth-jwt/tasks.md to mark T009 and T010 as complete.
- 🔁 Next prompts: Implement User Story 1 (T014-T028): authentication endpoints (signup, signin, signout), AuthService with password hashing and JWT generation, contract and integration tests.
- 🧠 Reflection: Migration approach follows best practices with idempotent SQL, rollback support, and migration tracking. Handled edge case of orphaned tasks gracefully. Windows Unicode encoding fix ensures cross-platform compatibility.

## Evaluation notes (flywheel)

- Failure modes observed: Initial Unicode encoding error on Windows console (✓ fixed with UTF-8 wrapper). Orphaned task prevented foreign key constraint (✓ resolved by creating test user).
- Graders run and results (PASS/FAIL): Migration 001 - PASS, Migration 002 - PASS, Schema verification - PASS, Foreign key verification - PASS, Index verification - PASS
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Consider adding database migration tests to verify rollback functionality. Add migration versioning to support branching strategies.
