"""
Pydantic request/response schemas for Task API.

[Task]: T009
[From]: specs/001-backend-task-api/contracts/schemas.json
[From]: specs/001-backend-task-api/data-model.md §Validation Rules
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator


class TaskCreate(BaseModel):
    """
    Request schema for creating a new task.

    Attributes:
        title: Short description of the task (required, 1-200 chars)
        description: Detailed information about the task (optional, max 1000 chars)
    """

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

    @validator("title")
    def title_not_empty(cls, v):
        """Validate that title is not empty or whitespace-only."""
        if not v or v.strip() == "":
            raise ValueError("Title cannot be empty or whitespace-only")
        return v.strip()


class TaskUpdate(BaseModel):
    """
    Request schema for updating an existing task.

    Attributes:
        title: Short description of the task (required, 1-200 chars)
        description: Detailed information about the task (optional, max 1000 chars)
    """

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

    @validator("title")
    def title_not_empty(cls, v):
        """Validate that title is not empty or whitespace-only."""
        if not v or v.strip() == "":
            raise ValueError("Title cannot be empty or whitespace-only")
        return v.strip()


class TaskResponse(BaseModel):
    """
    Response schema for task operations.

    Attributes:
        id: Unique task identifier
        user_id: Owner identifier
        title: Task title
        description: Task description (optional)
        completed: Completion status
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    id: int
    user_id: str
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Enable ORM mode for SQLModel compatibility
