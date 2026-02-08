"""
Script to manually initialize the database and create all tables.

Run this script to create the tasks table in your Neon database.

Usage:
    python init_database.py
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.db import init_db
from src.config import settings

def main():
    """Initialize the database and create all tables."""
    print("=" * 60)
    print("Database Initialization Script")
    print("=" * 60)
    print()

    # Display connection info (hide password)
    db_url = settings.database_url
    if '@' in db_url:
        # Hide password in display
        parts = db_url.split('@')
        user_part = parts[0].split('//')[1].split(':')[0]
        host_part = '@'.join(parts[1:])
        display_url = f"postgresql://{user_part}:****@{host_part}"
    else:
        display_url = db_url

    print(f"Database URL: {display_url}")
    print(f"Environment: {settings.environment}")
    print()

    try:
        print("Creating database tables...")
        init_db()
        print("[SUCCESS] Database tables created successfully!")
        print()
        print("Tables created:")
        print("  - tasks (id, user_id, title, description, completed, created_at, updated_at)")
        print()
        print("You can now start the FastAPI server:")
        print("  uvicorn src.main:app --reload")
        print()

    except Exception as e:
        print(f"[ERROR] Error creating tables: {e}")
        print()
        print("Please check:")
        print("  1. DATABASE_URL is correct in .env file")
        print("  2. Database exists and is accessible")
        print("  3. Network connection is working")
        sys.exit(1)

if __name__ == "__main__":
    main()
