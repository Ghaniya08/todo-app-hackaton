"""
Database migration runner for Todo application.

[Task]: T009, T010
[From]: specs/002-auth-jwt/data-model.md §Migration Strategy

This script runs SQL migrations in order and tracks which migrations
have been applied to prevent duplicate execution.

Usage:
    python migrations/run_migrations.py              # Run all pending migrations
    python migrations/run_migrations.py --rollback   # Rollback last migration
    python migrations/run_migrations.py --status     # Show migration status
"""

import sys
import os
from pathlib import Path

# Fix Windows console encoding for Unicode characters
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add parent directory to path to import from src
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import settings
import psycopg


def get_connection():
    """Get database connection using psycopg3."""
    # Convert SQLAlchemy URL to psycopg connection string
    db_url = settings.database_url
    # Remove the +psycopg prefix if present
    if '+psycopg://' in db_url:
        db_url = db_url.replace('+psycopg://', '://')
    elif 'postgresql://' in db_url:
        pass  # Already correct format
    else:
        raise ValueError(f"Unsupported database URL format: {db_url}")

    return psycopg.connect(db_url)


def create_migrations_table(conn):
    """Create migrations tracking table if it doesn't exist."""
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                id SERIAL PRIMARY KEY,
                migration_name VARCHAR(255) UNIQUE NOT NULL,
                applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        print("✓ Migrations tracking table ready")


def get_applied_migrations(conn):
    """Get list of already applied migrations."""
    with conn.cursor() as cur:
        cur.execute("SELECT migration_name FROM schema_migrations ORDER BY id")
        return [row[0] for row in cur.fetchall()]


def get_migration_files():
    """Get list of migration files in order."""
    migrations_dir = Path(__file__).parent
    migration_files = sorted(migrations_dir.glob("*.sql"))
    return [(f.stem, f) for f in migration_files]


def run_migration(conn, migration_name, migration_file):
    """Run a single migration file."""
    print(f"\n{'='*60}")
    print(f"Running migration: {migration_name}")
    print(f"{'='*60}")

    # Read migration file
    sql = migration_file.read_text(encoding='utf-8')

    # Extract only the UP migration part (before DOWN MIGRATION comment)
    if '-- DOWN MIGRATION' in sql:
        sql = sql.split('-- DOWN MIGRATION')[0]

    try:
        # Execute migration
        with conn.cursor() as cur:
            cur.execute(sql)

        # Record migration as applied
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO schema_migrations (migration_name) VALUES (%s)",
                (migration_name,)
            )

        conn.commit()
        print(f"✓ Migration {migration_name} completed successfully")
        return True

    except Exception as e:
        conn.rollback()
        print(f"✗ Migration {migration_name} failed: {e}")
        return False


def rollback_migration(conn, migration_name, migration_file):
    """Rollback a single migration."""
    print(f"\n{'='*60}")
    print(f"Rolling back migration: {migration_name}")
    print(f"{'='*60}")

    # Read migration file
    sql = migration_file.read_text(encoding='utf-8')

    # Extract DOWN migration part
    if '-- DOWN MIGRATION' not in sql:
        print(f"✗ No rollback script found for {migration_name}")
        return False

    # Get the rollback SQL (after DOWN MIGRATION comment)
    down_sql = sql.split('-- DOWN MIGRATION')[1]

    # Extract SQL commands (skip comments)
    lines = []
    for line in down_sql.split('\n'):
        line = line.strip()
        if line and not line.startswith('--'):
            lines.append(line)

    rollback_sql = '\n'.join(lines)

    if not rollback_sql.strip():
        print(f"✗ No rollback commands found for {migration_name}")
        return False

    try:
        # Execute rollback
        with conn.cursor() as cur:
            cur.execute(rollback_sql)

        # Remove migration record
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM schema_migrations WHERE migration_name = %s",
                (migration_name,)
            )

        conn.commit()
        print(f"✓ Migration {migration_name} rolled back successfully")
        return True

    except Exception as e:
        conn.rollback()
        print(f"✗ Rollback of {migration_name} failed: {e}")
        return False


def show_status(conn):
    """Show migration status."""
    print("\n" + "="*60)
    print("Migration Status")
    print("="*60)

    applied = get_applied_migrations(conn)
    all_migrations = get_migration_files()

    print(f"\nTotal migrations: {len(all_migrations)}")
    print(f"Applied: {len(applied)}")
    print(f"Pending: {len(all_migrations) - len(applied)}")

    print("\nMigrations:")
    for name, _ in all_migrations:
        status = "✓ Applied" if name in applied else "○ Pending"
        print(f"  {status}  {name}")

    print()


def main():
    """Main migration runner."""
    import argparse

    parser = argparse.ArgumentParser(description='Run database migrations')
    parser.add_argument('--rollback', action='store_true', help='Rollback last migration')
    parser.add_argument('--status', action='store_true', help='Show migration status')
    args = parser.parse_args()

    print("="*60)
    print("Database Migration Runner")
    print("="*60)
    print(f"Database: {settings.database_url.split('@')[1].split('/')[0] if '@' in settings.database_url else 'local'}")
    print()

    try:
        # Connect to database
        conn = get_connection()
        print("✓ Connected to database")

        # Create migrations tracking table
        create_migrations_table(conn)

        if args.status:
            # Show status
            show_status(conn)

        elif args.rollback:
            # Rollback last migration
            applied = get_applied_migrations(conn)
            if not applied:
                print("\n✗ No migrations to rollback")
                return

            last_migration = applied[-1]
            all_migrations = dict(get_migration_files())

            if last_migration not in all_migrations:
                print(f"\n✗ Migration file not found: {last_migration}")
                return

            success = rollback_migration(conn, last_migration, all_migrations[last_migration])
            if success:
                print("\n✓ Rollback completed successfully")
            else:
                print("\n✗ Rollback failed")
                sys.exit(1)

        else:
            # Run pending migrations
            applied = get_applied_migrations(conn)
            all_migrations = get_migration_files()

            pending = [(name, path) for name, path in all_migrations if name not in applied]

            if not pending:
                print("\n✓ All migrations are up to date")
                return

            print(f"\nFound {len(pending)} pending migration(s)")

            for name, path in pending:
                success = run_migration(conn, name, path)
                if not success:
                    print("\n✗ Migration failed, stopping")
                    sys.exit(1)

            print("\n" + "="*60)
            print("✓ All migrations completed successfully")
            print("="*60)

        conn.close()

    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
