"""
Helper script to create test user for existing tasks.

This script creates a test user with id 'user123' to match existing tasks
in the database, allowing the foreign key constraint to be added.

Usage:
    python migrations/create_test_user.py
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from src.config import settings
import psycopg
import bcrypt


def create_test_user():
    """Create test user to match existing tasks."""
    print("="*60)
    print("Create Test User")
    print("="*60)

    # Connect to database
    db_url = settings.database_url
    if '+psycopg://' in db_url:
        db_url = db_url.replace('+psycopg://', '://')

    conn = psycopg.connect(db_url)
    print("✓ Connected to database")

    try:
        # Check if user already exists
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM users WHERE id = %s", ('user123',))
            if cur.fetchone():
                print("✓ User 'user123' already exists")
                return

        # Hash password using bcrypt
        password = "password123"
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password_bytes, salt).decode('utf-8')

        # Create user
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO users (id, email, password_hash, name, created_at, updated_at)
                VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """, ('user123', 'test@example.com', hashed, 'Test User'))

        conn.commit()
        print("✓ Test user created successfully")
        print()
        print("User details:")
        print("  ID: user123")
        print("  Email: test@example.com")
        print("  Password: password123")
        print("  Name: Test User")
        print()
        print("You can now run the migrations:")
        print("  python migrations/run_migrations.py")

    except Exception as e:
        conn.rollback()
        print(f"✗ Error creating user: {e}")
        sys.exit(1)

    finally:
        conn.close()


if __name__ == "__main__":
    create_test_user()
