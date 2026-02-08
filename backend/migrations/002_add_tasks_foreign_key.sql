-- ============================================================================
-- Migration 002: Add Foreign Key Constraint to Tasks Table
-- ============================================================================
-- [Task]: T010
-- [From]: specs/002-auth-jwt/data-model.md §Database Schema Changes
-- [Feature]: 002-auth-jwt (Authentication & User Context)
-- [Date]: 2026-02-08
--
-- Purpose: Add foreign key constraint from tasks.user_id to users.id
--          to enforce referential integrity and enable cascade delete
--
-- Tables Modified:
--   - tasks (add foreign key constraint, verify indexes)
--
-- Constraints Added:
--   - fk_tasks_user_id (FOREIGN KEY with ON DELETE CASCADE)
--
-- Indexes Created:
--   - idx_tasks_user_id - for filtering tasks by user
--   - idx_tasks_user_completed - composite index for filtered queries
--
-- Dependencies: Migration 001 (users table must exist)
-- ============================================================================

-- ============================================================================
-- UP MIGRATION
-- ============================================================================

BEGIN;

-- Verify users table exists (dependency check)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'users') THEN
        RAISE EXCEPTION 'Migration failed: users table does not exist. Run migration 001 first.';
    END IF;
END $$;

-- Verify tasks table exists (should exist from Phase I)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'tasks') THEN
        RAISE EXCEPTION 'Migration failed: tasks table does not exist. Run Phase I migrations first.';
    END IF;
END $$;

-- Verify tasks.user_id column exists
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'tasks' AND column_name = 'user_id'
    ) THEN
        RAISE EXCEPTION 'Migration failed: tasks.user_id column does not exist';
    END IF;
END $$;

-- Create index on user_id if not exists (for filtering by user)
CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id);

-- Create composite index on (user_id, completed) for filtered queries
-- This optimizes queries like: SELECT * FROM tasks WHERE user_id = ? AND completed = ?
CREATE INDEX IF NOT EXISTS idx_tasks_user_completed ON tasks(user_id, completed);

-- Add foreign key constraint from tasks.user_id to users.id
-- ON DELETE CASCADE ensures tasks are deleted when user is deleted
-- Note: This will fail if there are existing tasks with user_id values
-- that don't exist in the users table (orphaned tasks)
DO $$
BEGIN
    -- Check if constraint already exists
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'fk_tasks_user_id'
        AND table_name = 'tasks'
    ) THEN
        -- Check for orphaned tasks before adding constraint
        IF EXISTS (
            SELECT 1 FROM tasks
            WHERE user_id NOT IN (SELECT id FROM users)
            AND user_id IS NOT NULL
        ) THEN
            RAISE WARNING 'Found tasks with user_id values that do not exist in users table';
            RAISE WARNING 'These orphaned tasks will prevent the foreign key constraint from being added';
            RAISE WARNING 'Please clean up orphaned tasks or create corresponding users first';
            RAISE EXCEPTION 'Migration failed: orphaned tasks exist';
        END IF;

        -- Add foreign key constraint
        ALTER TABLE tasks
        ADD CONSTRAINT fk_tasks_user_id
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

        RAISE NOTICE 'Foreign key constraint fk_tasks_user_id added successfully';
    ELSE
        RAISE NOTICE 'Foreign key constraint fk_tasks_user_id already exists, skipping';
    END IF;
END $$;

COMMIT;

-- Verify migration
DO $$
BEGIN
    -- Check if foreign key constraint exists
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'fk_tasks_user_id'
        AND table_name = 'tasks'
        AND constraint_type = 'FOREIGN KEY'
    ) THEN
        RAISE EXCEPTION 'Migration verification failed: fk_tasks_user_id constraint not found';
    END IF;

    -- Check if indexes exist
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_tasks_user_id') THEN
        RAISE EXCEPTION 'Migration verification failed: idx_tasks_user_id index not found';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_tasks_user_completed') THEN
        RAISE EXCEPTION 'Migration verification failed: idx_tasks_user_completed index not found';
    END IF;

    RAISE NOTICE 'Migration 002 completed successfully';
    RAISE NOTICE 'Foreign key constraint enforces: tasks.user_id -> users.id (ON DELETE CASCADE)';
END $$;

-- ============================================================================
-- DOWN MIGRATION (Rollback)
-- ============================================================================

-- To rollback this migration, run the following:
-- BEGIN;
-- ALTER TABLE tasks DROP CONSTRAINT IF EXISTS fk_tasks_user_id;
-- DROP INDEX IF EXISTS idx_tasks_user_completed;
-- DROP INDEX IF EXISTS idx_tasks_user_id;
-- COMMIT;

-- Note: This only removes the constraint and indexes, not the user_id column
-- The user_id column is part of the tasks table schema and should remain
