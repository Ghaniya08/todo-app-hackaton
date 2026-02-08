---
name: database-skill
description: Design scalable database schemas, create tables, and manage migrations efficiently. Use for backend and data-driven applications.
---

# Database Schema Design

## Instructions

1. **Schema planning**
   - Identify entities and relationships
   - Normalize data (avoid redundancy)
   - Define primary and foreign keys

2. **Table creation**
   - Use meaningful table and column names
   - Choose appropriate data types
   - Apply constraints (NOT NULL, UNIQUE, DEFAULT)

3. **Migrations**
   - Create versioned migrations
   - Support up and down (rollback) operations
   - Keep migrations atomic and reversible

## Best Practices
- Follow consistent naming conventions
- Prefer migrations over manual DB changes
- Index frequently queried columns
- Design with scalability in mind
- Document schema decisions

## Example Structure
```sql
-- Users table
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(150) UNIQUE NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Migration example
-- up
ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT true;

-- down
ALTER TABLE users DROP COLUMN is_active;
