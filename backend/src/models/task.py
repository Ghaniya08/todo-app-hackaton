"""
Task SQLModel entity for Backend Task API.

[Task]: T008
[From]: specs/001-backend-task-api/data-model.md §Entity: Task
[From]: specs/001-backend-task-api/spec.md §Key Entities
"""

from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class Task(SQLModel, table=True):
    """
    Task entity representing a user's todo item.

    Attributes:
        id: Unique task identifier (auto-increment)
        user_id: Owner identifier from authentication system
        title: Short description of the task (required, max 200 chars)
        description: Detailed information about the task (optional, max 1000 chars)
        completed: Completion status (true = done, false = pending)
        created_at: UTC timestamp when task was created
        updated_at: UTC timestamp when task was last modified
    """

    __tablename__ = "tasks"

    # Primary Key
    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Unique task identifier (auto-increment)",
    )

    # Foreign Key (User Ownership)
    user_id: str = Field(
        index=True,
        max_length=255,
        description="Owner identifier from authentication system",
    )

    # Task Content
    title: str = Field(
        min_length=1,
        max_length=200,
        description="Short description of the task (required)",
    )

    description: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Detailed information about the task (optional)",
    )

    # Task Status
    completed: bool = Field(
        default=False,
        description="Completion status (true = done, false = pending)",
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="UTC timestamp when task was created",
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow},
        description="UTC timestamp when task was last modified",
    )
