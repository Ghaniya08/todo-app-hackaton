"""
Configuration management for Backend Task API.

[Task]: T006, T008
[From]: specs/001-backend-task-api/plan.md §Technical Context
[From]: specs/001-backend-task-api/research.md §Research Item 1
[From]: specs/002-auth-jwt/plan.md §Technical Context
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""

    def __init__(self):
        """Initialize settings and validate required configuration."""
        self.database_url: str = self._get_required_env("DATABASE_URL")
        self.environment: str = os.getenv("ENVIRONMENT", "development")
        self.log_level: str = os.getenv("LOG_LEVEL", "info")

        # [Task]: T008 - JWT Authentication Configuration
        # [From]: specs/002-auth-jwt/data-model.md §Security Constraints
        self.better_auth_secret: str = self._get_required_env("BETTER_AUTH_SECRET")
        self._validate_auth_secret()

    def _get_required_env(self, key: str) -> str:
        """
        Get required environment variable or raise error.

        Args:
            key: Environment variable name

        Returns:
            Environment variable value

        Raises:
            ValueError: If required environment variable is not set
        """
        value = os.getenv(key)
        if not value:
            raise ValueError(
                f"Required environment variable {key} is not set. "
                f"Please configure it in your .env file."
            )
        return value

    def _validate_auth_secret(self) -> None:
        """
        Validate BETTER_AUTH_SECRET meets security requirements.

        [Task]: T008
        [From]: specs/002-auth-jwt/plan.md §Security Requirements

        Raises:
            ValueError: If secret is too short (minimum 32 characters required)
        """
        if len(self.better_auth_secret) < 32:
            raise ValueError(
                "BETTER_AUTH_SECRET must be at least 32 characters long for security. "
                f"Current length: {len(self.better_auth_secret)} characters. "
                "Please generate a secure secret using: openssl rand -base64 32"
            )

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"


# Global settings instance
settings = Settings()
