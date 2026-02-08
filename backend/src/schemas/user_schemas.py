"""
Pydantic request/response schemas for User Authentication API.

[Task]: T007
[From]: specs/002-auth-jwt/contracts/auth-api.yaml
[From]: specs/002-auth-jwt/data-model.md §Validation Rules
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, validator


class UserCreate(BaseModel):
    """
    Request schema for user signup (account creation).

    Attributes:
        email: User's email address (must be unique and valid format)
        password: User's password (minimum 8 characters)
        name: User's display name (optional)
    """

    email: EmailStr = Field(
        description="User's email address (must be unique)",
        example="alice@example.com",
    )
    password: str = Field(
        min_length=8,
        max_length=128,
        description="User's password (minimum 8 characters)",
        example="password123",
    )
    name: Optional[str] = Field(
        default=None,
        max_length=255,
        description="User's display name (optional)",
        example="Alice",
    )

    @validator("password")
    def password_not_empty(cls, v):
        """Validate that password is not empty or whitespace-only."""
        if not v or v.strip() == "":
            raise ValueError("Password cannot be empty or whitespace-only")
        return v

    @validator("name")
    def name_strip_whitespace(cls, v):
        """Strip leading/trailing whitespace from name if provided."""
        if v:
            return v.strip() if v.strip() else None
        return v


class SignInRequest(BaseModel):
    """
    Request schema for user signin (authentication).

    Attributes:
        email: User's email address
        password: User's password
    """

    email: EmailStr = Field(
        description="User's email address",
        example="alice@example.com",
    )
    password: str = Field(
        description="User's password",
        example="password123",
    )


class UserResponse(BaseModel):
    """
    Response schema for user operations.

    SECURITY: Never expose password_hash in API responses.

    Attributes:
        id: Unique user identifier (UUID)
        email: User's email address
        name: User's display name (optional)
        created_at: Account creation timestamp
    """

    id: str = Field(
        description="Unique user identifier (UUID)",
        example="550e8400-e29b-41d4-a716-446655440000",
    )
    email: str = Field(
        description="User's email address",
        example="alice@example.com",
    )
    name: Optional[str] = Field(
        default=None,
        description="User's display name",
        example="Alice",
    )
    created_at: datetime = Field(
        description="Account creation timestamp",
        example="2026-02-08T20:30:00Z",
    )

    class Config:
        from_attributes = True  # Enable ORM mode for SQLModel compatibility
