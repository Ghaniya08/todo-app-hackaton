-- ============================================================================
-- Migration 001: Create Users Table
-- ============================================================================
-- [Task]: T009
-- [From]: specs/002-auth-jwt/data-model.md §Database Schema Changes
-- [Feature]: 002-auth-jwt (Authentication & User Context)
-- [Date]: 2026-02-08
--
-- Purpose: Create users table for authentication with Better Auth + JWT
--
-- Tables Created:
--   - users (id, email, password_hash, name, created_at, updated_at)
--
-- Indexes Created:
--   - idx_users_email (UNIQUE) - for login lookup
--   - idx_users_created_at - for analytics
--
-- Dependencies: None (first migration for auth feature)
-- ============================================================================

-- ============================================================================
-- UP MIGRATION
-- ============================================================================

BEGIN;

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(255) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create unique index on email for fast login lookup
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Create index on created_at for analytics queries
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);

-- Add comment to table
COMMENT ON TABLE users IS 'User accounts with authentication credentials';
COMMENT ON COLUMN users.id IS 'Unique user identifier (UUID from Better Auth)';
COMMENT ON COLUMN users.email IS 'User email address for authentication (unique)';
COMMENT ON COLUMN users.password_hash IS 'Bcrypt-hashed password (never store plain text)';
COMMENT ON COLUMN users.name IS 'User display name (optional)';
COMMENT ON COLUMN users.created_at IS 'Account creation timestamp';
COMMENT ON COLUMN users.updated_at IS 'Last account update timestamp';

COMMIT;

-- Verify migration
DO $$
BEGIN
    -- Check if users table exists
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'users') THEN
        RAISE EXCEPTION 'Migration failed: users table was not created';
    END IF;

    -- Check if email index exists
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_users_email') THEN
        RAISE EXCEPTION 'Migration failed: idx_users_email index was not created';
    END IF;

    RAISE NOTICE 'Migration 001 completed successfully';
END $$;

-- ============================================================================
-- DOWN MIGRATION (Rollback)
-- ============================================================================

-- To rollback this migration, run the following:
-- BEGIN;
-- DROP TABLE IF EXISTS users CASCADE;
-- COMMIT;

-- WARNING: This will delete all user data and cascade to tasks table
-- (if foreign key constraint exists from migration 002)
