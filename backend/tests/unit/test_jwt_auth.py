"""
Unit tests for JWT authentication middleware.

[Task]: T011, T012
[From]: specs/002-auth-jwt/plan.md §JWT Verification
"""

import pytest
import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException
from src.middleware.jwt_auth import verify_jwt, create_jwt_token
from src.config import settings


class TestJWTTokenCreation:
    """Test JWT token creation."""

    def test_create_jwt_token_valid(self):
        """Test creating a valid JWT token."""
        user_id = "test-user-123"
        token = create_jwt_token(user_id, expires_in_hours=24)

        # Verify token can be decoded
        payload = jwt.decode(
            token,
            settings.better_auth_secret,
            algorithms=["HS256"],
        )

        assert payload["sub"] == user_id
        assert "exp" in payload
        assert "iat" in payload

    def test_create_jwt_token_custom_expiration(self):
        """Test creating a JWT token with custom expiration."""
        user_id = "test-user-456"
        token = create_jwt_token(user_id, expires_in_hours=1)

        payload = jwt.decode(
            token,
            settings.better_auth_secret,
            algorithms=["HS256"],
        )

        # Verify expiration is approximately 1 hour from now
        exp_time = datetime.fromtimestamp(payload["exp"])
        now = datetime.utcnow()
        time_diff = (exp_time - now).total_seconds()

        # Should be close to 1 hour (3600 seconds), allow 10 second variance
        assert 3590 <= time_diff <= 3610


class TestJWTVerification:
    """Test JWT token verification."""

    @pytest.mark.asyncio
    async def test_verify_jwt_valid_token_in_header(self, test_jwt_token):
        """Test verifying a valid JWT token from Authorization header."""
        from fastapi import Request
        from fastapi.security import HTTPAuthorizationCredentials

        # Mock request
        request = Request(scope={"type": "http", "headers": []})

        # Mock authorization credentials
        auth = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=test_jwt_token,
        )

        # Verify token
        user_id = await verify_jwt(request, authorization=auth, token=None)

        assert user_id == "test-user-uuid-12345"

    @pytest.mark.asyncio
    async def test_verify_jwt_valid_token_in_cookie(self, test_jwt_token):
        """Test verifying a valid JWT token from cookie."""
        from fastapi import Request

        # Mock request
        request = Request(scope={"type": "http", "headers": []})

        # Verify token from cookie
        user_id = await verify_jwt(request, authorization=None, token=test_jwt_token)

        assert user_id == "test-user-uuid-12345"

    @pytest.mark.asyncio
    async def test_verify_jwt_missing_token(self):
        """Test verifying with no token raises 401."""
        from fastapi import Request

        request = Request(scope={"type": "http", "headers": []})

        with pytest.raises(HTTPException) as exc_info:
            await verify_jwt(request, authorization=None, token=None)

        assert exc_info.value.status_code == 401
        assert "Missing authentication token" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_verify_jwt_expired_token(self):
        """Test verifying an expired token raises 401."""
        from fastapi import Request

        # Create an expired token (expired 1 hour ago)
        user_id = "test-user-789"
        now = datetime.utcnow()
        expired_time = now - timedelta(hours=1)

        payload = {
            "sub": user_id,
            "exp": expired_time,
            "iat": now - timedelta(hours=2),
        }

        expired_token = jwt.encode(
            payload,
            settings.better_auth_secret,
            algorithm="HS256",
        )

        request = Request(scope={"type": "http", "headers": []})

        with pytest.raises(HTTPException) as exc_info:
            await verify_jwt(request, authorization=None, token=expired_token)

        assert exc_info.value.status_code == 401
        assert "expired" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_verify_jwt_invalid_signature(self):
        """Test verifying a token with invalid signature raises 401."""
        from fastapi import Request

        # Create a token with wrong secret
        user_id = "test-user-999"
        payload = {
            "sub": user_id,
            "exp": datetime.utcnow() + timedelta(hours=24),
            "iat": datetime.utcnow(),
        }

        invalid_token = jwt.encode(
            payload,
            "wrong-secret-key-12345678901234567890",
            algorithm="HS256",
        )

        request = Request(scope={"type": "http", "headers": []})

        with pytest.raises(HTTPException) as exc_info:
            await verify_jwt(request, authorization=None, token=invalid_token)

        assert exc_info.value.status_code == 401
        assert "Invalid authentication token" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_verify_jwt_missing_sub_claim(self):
        """Test verifying a token without 'sub' claim raises 401."""
        from fastapi import Request

        # Create a token without 'sub' claim
        payload = {
            "exp": datetime.utcnow() + timedelta(hours=24),
            "iat": datetime.utcnow(),
        }

        invalid_token = jwt.encode(
            payload,
            settings.better_auth_secret,
            algorithm="HS256",
        )

        request = Request(scope={"type": "http", "headers": []})

        with pytest.raises(HTTPException) as exc_info:
            await verify_jwt(request, authorization=None, token=invalid_token)

        assert exc_info.value.status_code == 401
        assert "Invalid authentication token" in exc_info.value.detail
