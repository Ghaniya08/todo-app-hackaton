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

        # [Task]: T002 - AI Chat Agent Configuration (Phase III)
        # [From]: specs/004-ai-chat-agent/plan.md §Dependencies
        # Supports: openai, gemini, groq
        self.ai_provider: str = os.getenv("AI_PROVIDER", "gemini")
        self.ai_api_key: str = os.getenv("AI_API_KEY") or os.getenv("OPENAI_API_KEY", "")
        self.ai_model: str = os.getenv("AI_MODEL", self._get_default_model())
        self.ai_base_url: Optional[str] = os.getenv("AI_BASE_URL", self._get_default_base_url())
        self.chat_context_limit: int = int(os.getenv("CHAT_CONTEXT_LIMIT", "20"))
        self.chat_timeout_seconds: int = int(os.getenv("CHAT_TIMEOUT_SECONDS", "30"))

        # Legacy support
        self.openai_api_key: str = self.ai_api_key
        self.openai_model: str = self.ai_model

    def _get_default_model(self) -> str:
        """Get default model based on provider."""
        models = {
            "openai": "gpt-4o-mini",
            "gemini": "gemini-2.0-flash",
            "groq": "llama-3.3-70b-versatile",
        }
        return models.get(self.ai_provider, "gpt-4o-mini")

    def _get_default_base_url(self) -> Optional[str]:
        """Get default base URL based on provider."""
        urls = {
            "openai": None,  # Uses default
            "gemini": "https://generativelanguage.googleapis.com/v1beta/openai/",
            "groq": "https://api.groq.com/openai/v1",
        }
        return urls.get(self.ai_provider)

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
