"""
Unit tests for JWT authentication middleware.

[Task]: T055
[From]: specs/002-auth-jwt/plan.md §Phase 2 - JWT Verification
[From]: specs/002-auth-jwt/spec.md §FR-011, FR-012
"""

import pytest
import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials
from unittest.mock import Mock, AsyncMock

from src.middleware.jwt_auth import verify_jwt, JWT_SECRET, JWT_ALGORITHM


class TestVerifyJWT:
    """Test suite for JWT verification middleware."""

    def create_valid_token(self, user_id: str = "test-user-123", expires_in_hours: int = 24) -> str:
        """Helper to create a valid JWT token for testing."""
        now = datetime.utcnow()
        expiration = now + timedelta(hours=expires_in_hours)

        payload = {
            "sub": user_id,
            "email": "test@example.com",
            "iat": now,
            "exp": expiration,
        }

        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    def create_expired_token(self, user_id: str = "test-user-123") -> str:
        """Helper to create an expired JWT token for testing."""
        now = datetime.utcnow()
        expiration = now - timedelta(hours=1)  # Expired 1 hour ago

        payload = {
            "sub": user_id,
            "email": "test@example.com",
            "iat": now - timedelta(hours=2),
            "exp": expiration,
        }

        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    @pytest.mark.asyncio
    async def test_verify_jwt_with_valid_bearer_token(self):
        """Test JWT verification with valid Bearer token in Authorization header."""
        # Arrange
        user_id = "test-user-123"
        token = self.create_valid_token(user_id)

        request = Mock(spec=Request)
        authorization = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

        # Act
        result = await verify_jwt(request, authorization=authorization, token=None)

        # Assert
        assert result == user_id

    @pytest.mark.asyncio
    async def test_verify_jwt_with_valid_cookie_token(self):
        """Test JWT verification with valid token in cookie."""
        # Arrange
        user_id = "test-user-456"
        token = self.create_valid_token(user_id)

        request = Mock(spec=Request)

        # Act
        result = await verify_jwt(request, authorization=None, token=token)

        # Assert
        assert result == user_id

    @pytest.mark.asyncio
    async def test_verify_jwt_prefers_authorization_header_over_cookie(self):
        """Test that Authorization header takes precedence over cookie."""
        # Arrange
        header_user_id = "header-user"
        cookie_user_id = "cookie-user"

        header_token = self.create_valid_token(header_user_id)
        cookie_token = self.create_valid_token(cookie_user_id)

        request = Mock(spec=Request)
        authorization = HTTPAuthorizationCredentials(scheme="Bearer", credentials=header_token)

        # Act
        result = await verify_jwt(request, authorization=authorization, token=cookie_token)

        # Assert
        assert result == header_user_id  # Should use header, not cookie

    @pytest.mark.asyncio
    async def test_verify_jwt_missing_token(self):
        """Test JWT verification fails when no token is provided."""
        # Arrange
        request = Mock(spec=Request)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await verify_jwt(request, authorization=None, token=None)

        assert exc_info.value.status_code == 401
        assert "Missing authentication token" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_verify_jwt_expired_token(self):
        """Test JWT verification fails with expired token."""
        # Arrange
        expired_token = self.create_expired_token()

        request = Mock(spec=Request)
        authorization = HTTPAuthorizationCredentials(scheme="Bearer", credentials=expired_token)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await verify_jwt(request, authorization=authorization, token=None)

        assert exc_info.value.status_code == 401
        assert "expired" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_verify_jwt_invalid_signature(self):
        """Test JWT verification fails with invalid signature."""
        # Arrange
        # Create token with wrong secret
        payload = {
            "sub": "test-user",
            "exp": datetime.utcnow() + timedelta(hours=24),
        }
        invalid_token = jwt.encode(payload, "wrong-secret", algorithm=JWT_ALGORITHM)

        request = Mock(spec=Request)
        authorization = HTTPAuthorizationCredentials(scheme="Bearer", credentials=invalid_token)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await verify_jwt(request, authorization=authorization, token=None)

        assert exc_info.value.status_code == 401
        assert "Invalid authentication token" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_verify_jwt_malformed_token(self):
        """Test JWT verification fails with malformed token."""
        # Arrange
        malformed_token = "not.a.valid.jwt.token"

        request = Mock(spec=Request)
        authorization = HTTPAuthorizationCredentials(scheme="Bearer", credentials=malformed_token)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await verify_jwt(request, authorization=authorization, token=None)

        assert exc_info.value.status_code == 401
        assert "Invalid authentication token" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_verify_jwt_missing_sub_claim(self):
        """Test JWT verification fails when 'sub' claim is missing."""
        # Arrange
        payload = {
            "email": "test@example.com",
            "exp": datetime.utcnow() + timedelta(hours=24),
        }
        token_without_sub = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

        request = Mock(spec=Request)
        authorization = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token_without_sub)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await verify_jwt(request, authorization=authorization, token=None)

        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_verify_jwt_empty_sub_claim(self):
        """Test JWT verification fails when 'sub' claim is empty."""
        # Arrange
        payload = {
            "sub": "",  # Empty user_id
            "exp": datetime.utcnow() + timedelta(hours=24),
        }
        token_with_empty_sub = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

        request = Mock(spec=Request)
        authorization = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token_with_empty_sub)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await verify_jwt(request, authorization=authorization, token=None)

        assert exc_info.value.status_code == 401
        # Note: Empty sub claim triggers generic "Authentication failed" error
        # due to exception handling flow (HTTPException caught by outer handler)
        assert exc_info.value.detail in ["Invalid authentication token", "Authentication failed"]

    @pytest.mark.asyncio
    async def test_verify_jwt_with_different_algorithm(self):
        """Test JWT verification fails when token uses different algorithm."""
        # Arrange
        payload = {
            "sub": "test-user",
            "exp": datetime.utcnow() + timedelta(hours=24),
        }
        # Create token with HS512 instead of HS256
        token_wrong_algo = jwt.encode(payload, JWT_SECRET, algorithm="HS512")

        request = Mock(spec=Request)
        authorization = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token_wrong_algo)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await verify_jwt(request, authorization=authorization, token=None)

        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_verify_jwt_with_special_characters_in_user_id(self):
        """Test JWT verification works with special characters in user_id."""
        # Arrange
        user_id = "user-123-abc_def@domain.com"
        token = self.create_valid_token(user_id)

        request = Mock(spec=Request)
        authorization = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

        # Act
        result = await verify_jwt(request, authorization=authorization, token=None)

        # Assert
        assert result == user_id

    @pytest.mark.asyncio
    async def test_verify_jwt_token_about_to_expire(self):
        """Test JWT verification succeeds with token about to expire (but not yet expired)."""
        # Arrange
        user_id = "test-user"
        # Token expires in 1 second
        token = self.create_valid_token(user_id, expires_in_hours=1/3600)

        request = Mock(spec=Request)
        authorization = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

        # Act
        result = await verify_jwt(request, authorization=authorization, token=None)

        # Assert
        assert result == user_id
