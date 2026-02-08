# Database Migrations

This directory contains SQL migration scripts for the Todo application database.

## Migration Files

Migrations are numbered sequentially and include both upgrade (up) and rollback (down) scripts.

### Migration 001: Create Users Table
- **File**: `001_create_users_table.sql`
- **Purpose**: Create the users table with authentication fields
- **Tables**: users
- **Indexes**: idx_users_email (unique), idx_users_created_at

### Migration 002: Add Foreign Key to Tasks
- **File**: `002_add_tasks_foreign_key.sql`
- **Purpose**: Add foreign key constraint from tasks.user_id to users.id
- **Tables**: tasks (modified)
- **Constraints**: fk_tasks_user_id (ON DELETE CASCADE)
- **Indexes**: idx_tasks_user_id, idx_tasks_user_completed

## Running Migrations

### Using psql (Neon Database)

```bash
# Set your database URL
export DATABASE_URL="postgresql://user:password@host/database?sslmode=require"

# Run migration 001 (up)
psql $DATABASE_URL -f migrations/001_create_users_table.sql

# Run migration 002 (up)
psql $DATABASE_URL -f migrations/002_add_tasks_foreign_key.sql
```

### Using Python Script

```bash
# Run all migrations
python migrations/run_migrations.py

# Rollback last migration
python migrations/run_migrations.py --rollback
```

## Rollback Migrations

Each migration file contains both UP and DOWN sections. To rollback:

```bash
# Rollback migration 002
psql $DATABASE_URL -c "$(grep -A 100 '-- DOWN MIGRATION' migrations/002_add_tasks_foreign_key.sql | tail -n +2)"

# Rollback migration 001
psql $DATABASE_URL -c "$(grep -A 100 '-- DOWN MIGRATION' migrations/001_create_users_table.sql | tail -n +2)"
```

## Migration Order

Migrations must be run in order:
1. 001_create_users_table.sql (creates users table)
2. 002_add_tasks_foreign_key.sql (adds FK from tasks to users)

## Verification

After running migrations, verify the schema:

```sql
-- Check users table exists
SELECT table_name, column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'users'
ORDER BY ordinal_position;

-- Check foreign key constraint exists
SELECT
    tc.constraint_name,
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
    AND tc.table_name = 'tasks';

-- Check indexes
SELECT
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename IN ('users', 'tasks')
ORDER BY tablename, indexname;
```

## Notes

- All migrations are idempotent (can be run multiple times safely)
- Use `IF NOT EXISTS` for CREATE statements
- Use `IF EXISTS` for DROP statements
- Always test migrations on a copy of production data first
- Keep migrations small and focused on a single change
- Document breaking changes clearly

## References

- [Task]: T009, T010
- [From]: specs/002-auth-jwt/data-model.md
- [From]: specs/002-auth-jwt/tasks.md
