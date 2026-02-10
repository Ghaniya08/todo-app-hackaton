"""
Conversation SQLModel entity for AI Chat Agent.

[Task]: T005
[From]: specs/004-ai-chat-agent/data-model.md §Entity: Conversation
[From]: specs/004-ai-chat-agent/spec.md §Key Entities
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel


class Conversation(SQLModel, table=True):
    """
    Conversation entity representing a chat session.

    Attributes:
        id: Unique conversation identifier (UUID, auto-generated)
        user_id: Owner identifier from authentication system
        title: Optional conversation title (auto-generated from first message)
        created_at: UTC timestamp when conversation was created
        updated_at: UTC timestamp when conversation was last modified
    """

    __tablename__ = "conversations"

    # Primary Key
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        description="Unique conversation identifier",
    )

    # Foreign Key (User Ownership)
    user_id: str = Field(
        index=True,
        max_length=255,
        description="Owner identifier from authentication system",
    )

    # Conversation Metadata
    title: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Optional conversation title",
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="UTC timestamp when conversation was created",
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow},
        description="UTC timestamp when conversation was last modified",
    )
