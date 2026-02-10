# Data Model: AI Chat Agent & Integration

**Feature**: 004-ai-chat-agent
**Date**: 2026-02-10
**Status**: Complete

## Entity Overview

This feature introduces two new entities to support conversation persistence:

| Entity | Purpose | Relationship |
|--------|---------|--------------|
| Conversation | Chat session container | One user has many conversations |
| Message | Individual chat message | One conversation has many messages |

## Entity: Conversation

Represents a chat session between a user and the AI assistant.

### Attributes

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique conversation identifier |
| user_id | String(255) | NOT NULL, indexed | Owner of the conversation |
| title | String(200) | nullable | Optional conversation title (auto-generated from first message) |
| created_at | Timestamp | NOT NULL, default now | When conversation was created |
| updated_at | Timestamp | NOT NULL, auto-update | When conversation was last modified |

### Indexes

- `idx_conversations_user_id` on `user_id` - Fast lookup by user
- `idx_conversations_updated_at` on `updated_at` - Sort by recent activity

### SQLModel Definition

```python
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel

class Conversation(SQLModel, table=True):
    """
    Conversation entity representing a chat session.

    [Task]: T-XXX
    [From]: specs/004-ai-chat-agent/data-model.md §Entity: Conversation
    """
    __tablename__ = "conversations"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique conversation identifier"
    )

    user_id: str = Field(
        index=True,
        max_length=255,
        description="Owner identifier from authentication system"
    )

    title: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Optional conversation title"
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When conversation was created"
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow},
        description="When conversation was last modified"
    )
```

## Entity: Message

Represents a single message in a conversation.

### Attributes

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK, auto-generated | Unique message identifier |
| conversation_id | UUID | FK → conversations.id, NOT NULL, indexed | Parent conversation |
| role | String(20) | NOT NULL, enum | Message role: 'user', 'assistant', 'tool' |
| content | Text | NOT NULL | Message content |
| tool_calls | JSONB | nullable | Tool call details (for assistant messages) |
| created_at | Timestamp | NOT NULL, default now | When message was created |

### Indexes

- `idx_messages_conversation_id` on `conversation_id` - Fast lookup by conversation
- `idx_messages_created_at` on `created_at` - Sort by time

### Role Enum Values

| Value | Description |
|-------|-------------|
| `user` | Message from the user |
| `assistant` | Response from the AI agent |
| `tool` | Tool execution result |

### SQLModel Definition

```python
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel, JSON

class Message(SQLModel, table=True):
    """
    Message entity representing a chat message.

    [Task]: T-XXX
    [From]: specs/004-ai-chat-agent/data-model.md §Entity: Message
    """
    __tablename__ = "messages"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique message identifier"
    )

    conversation_id: UUID = Field(
        foreign_key="conversations.id",
        index=True,
        description="Parent conversation reference"
    )

    role: str = Field(
        max_length=20,
        description="Message role: user, assistant, or tool"
    )

    content: str = Field(
        description="Message content"
    )

    tool_calls: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_type=JSON,
        description="Tool call details for assistant messages"
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When message was created"
    )
```

## Relationships

### Entity Relationship Diagram

```
┌─────────────────┐         ┌─────────────────┐
│      User       │         │   Conversation  │
│  (from auth)    │ 1────N  │                 │
│                 │         │ - id (PK)       │
│ - id            │─────────│ - user_id (FK)  │
│ - email         │         │ - title         │
│ - name          │         │ - created_at    │
└─────────────────┘         │ - updated_at    │
                            └────────┬────────┘
                                     │
                                     │ 1
                                     │
                                     │ N
                            ┌────────┴────────┐
                            │     Message     │
                            │                 │
                            │ - id (PK)       │
                            │ - conversation_ │
                            │   id (FK)       │
                            │ - role          │
                            │ - content       │
                            │ - tool_calls    │
                            │ - created_at    │
                            └─────────────────┘
```

### Relationship Rules

1. **User → Conversation**: One-to-Many
   - A user can have multiple conversations
   - Each conversation belongs to exactly one user
   - Deleting a user should cascade delete conversations

2. **Conversation → Message**: One-to-Many
   - A conversation can have multiple messages
   - Each message belongs to exactly one conversation
   - Deleting a conversation should cascade delete messages

## Query Patterns

### 1. Get User's Conversations

```python
def get_user_conversations(session: Session, user_id: str) -> List[Conversation]:
    """Get all conversations for a user, ordered by most recent."""
    statement = (
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
    )
    return session.exec(statement).all()
```

### 2. Get Conversation Messages

```python
def get_conversation_messages(
    session: Session,
    conversation_id: UUID,
    limit: int = 20
) -> List[Message]:
    """Get recent messages for a conversation."""
    statement = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    messages = session.exec(statement).all()
    return list(reversed(messages))  # Chronological order
```

### 3. Add Message to Conversation

```python
def add_message(
    session: Session,
    conversation_id: UUID,
    role: str,
    content: str,
    tool_calls: Optional[Dict] = None
) -> Message:
    """Add a new message to a conversation."""
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        tool_calls=tool_calls
    )
    session.add(message)

    # Update conversation updated_at
    conversation = session.get(Conversation, conversation_id)
    if conversation:
        conversation.updated_at = datetime.utcnow()
        session.add(conversation)

    session.commit()
    session.refresh(message)
    return message
```

### 4. Create New Conversation

```python
def create_conversation(
    session: Session,
    user_id: str,
    title: Optional[str] = None
) -> Conversation:
    """Create a new conversation for a user."""
    conversation = Conversation(
        user_id=user_id,
        title=title
    )
    session.add(conversation)
    session.commit()
    session.refresh(conversation)
    return conversation
```

## Security Constraints

### User Isolation

All queries MUST filter by `user_id` to enforce user isolation:

```python
# ✅ CORRECT: Filter by user_id
select(Conversation).where(
    Conversation.user_id == authenticated_user_id
)

# ❌ WRONG: No user filter
select(Conversation).where(
    Conversation.id == conversation_id
)
```

### Ownership Verification

Before accessing a conversation, verify ownership:

```python
def verify_conversation_ownership(
    session: Session,
    conversation_id: UUID,
    user_id: str
) -> bool:
    """Verify user owns the conversation."""
    conversation = session.get(Conversation, conversation_id)
    return conversation and conversation.user_id == user_id
```

## Migration Strategy

### Forward Migration

```sql
-- Create conversations table
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255) NOT NULL,
    title VARCHAR(200),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_updated_at ON conversations(updated_at);

-- Create messages table
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'tool')),
    content TEXT NOT NULL,
    tool_calls JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);
```

### Rollback Migration

```sql
DROP TABLE IF EXISTS messages;
DROP TABLE IF EXISTS conversations;
```

## Data Retention

- Conversations and messages persist indefinitely (no auto-delete)
- Future enhancement: Add conversation archiving feature
- Consider periodic cleanup of very old conversations (>1 year)
