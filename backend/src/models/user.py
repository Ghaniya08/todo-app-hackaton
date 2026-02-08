"""
User SQLModel entity for Authentication & User Context.

[Task]: T006
[From]: specs/002-auth-jwt/data-model.md §Entity: User
[From]: specs/002-auth-jwt/spec.md §Key Entities
"""

from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    """
    User entity representing a registered user account.

    Attributes:
        id: Unique user identifier (UUID string from Better Auth)
        email: User's email address for authentication (unique)
        password_hash: Bcrypt-hashed password (never store plain text)
        name: User's display name (optional)
        created_at: UTC timestamp when account was created
        updated_at: UTC timestamp when account was last modified
    """

    __tablename__ = "users"

    # Primary Key
    id: str = Field(
        primary_key=True,
        max_length=255,
        description="Unique user identifier (UUID from Better Auth)",
    )

    # Authentication Credentials
    email: str = Field(
        unique=True,
        index=True,
        max_length=255,
        description="User's email address for authentication (unique)",
    )

    password_hash: str = Field(
        max_length=255,
        description="Bcrypt-hashed password (never store plain text)",
    )

    # User Profile
    name: Optional[str] = Field(
        default=None,
        max_length=255,
        description="User's display name (optional)",
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="UTC timestamp when account was created",
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow},
        description="UTC timestamp when account was last modified",
    )
