"""
Message SQLModel entity for AI Chat Agent.

[Task]: T006
[From]: specs/004-ai-chat-agent/data-model.md §Entity: Message
[From]: specs/004-ai-chat-agent/spec.md §Key Entities
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel, Column, JSON


class Message(SQLModel, table=True):
    """
    Message entity representing a chat message in a conversation.

    Attributes:
        id: Unique message identifier (UUID, auto-generated)
        conversation_id: Parent conversation reference
        role: Message role: 'user', 'assistant', or 'tool'
        content: Message content text
        tool_calls: Tool call details for assistant messages (JSONB)
        created_at: UTC timestamp when message was created
    """

    __tablename__ = "messages"

    # Primary Key
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique message identifier",
    )

    # Foreign Key (Conversation Reference)
    conversation_id: UUID = Field(
        foreign_key="conversations.id",
        index=True,
        description="Parent conversation reference",
    )

    # Message Content
    role: str = Field(
        max_length=20,
        description="Message role: user, assistant, or tool",
    )

    content: str = Field(
        description="Message content text",
    )

    # Tool Calls (for assistant messages)
    tool_calls: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        sa_column=Column(JSON),
        description="Tool call details for assistant messages",
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="UTC timestamp when message was created",
    )
