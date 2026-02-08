"""
JWT authentication middleware for Backend Task API.

[Task]: T011
[From]: specs/002-auth-jwt/plan.md §Phase 2 - JWT Verification
[From]: specs/002-auth-jwt/data-model.md §Security Constraints
"""

import jwt
from datetime import datetime
from typing import Optional
from fastapi import HTTPException, status, Request, Cookie, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ..config import settings
import logging

logger = logging.getLogger(__name__)

# JWT Configuration
JWT_ALGORITHM = "HS256"
JWT_SECRET = settings.better_auth_secret

# Optional Bearer token scheme (for Authorization header)
bearer_scheme = HTTPBearer(auto_error=False)


async def verify_jwt(
    request: Request,
    authorization: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    token: Optional[str] = Cookie(default=None),
) -> str:
    """
    Verify JWT token and extract user_id.

    [Task]: T011
    [From]: specs/002-auth-jwt/plan.md §JWT Verification Flow

    This dependency extracts the JWT token from either:
    1. Authorization header (Bearer token)
    2. Cookie (httpOnly cookie named 'token')

    It then verifies the token signature, checks expiration,
    and extracts the user_id from the 'sub' claim.

    Args:
        request: FastAPI request object
        authorization: Optional Bearer token from Authorization header
        token: Optional JWT token from cookie

    Returns:
        str: Authenticated user_id extracted from JWT payload

    Raises:
        HTTPException(401): If token is missing, invalid, expired, or malformed

    Security Notes:
        - Token signature verified using BETTER_AUTH_SECRET with HS256
        - Expiration timestamp checked against current time
        - User_id extracted from 'sub' claim (JWT standard)
        - Generic error messages to avoid information leakage
    """
    # Extract token from Authorization header or cookie
    jwt_token: Optional[str] = None

    if authorization and authorization.credentials:
        jwt_token = authorization.credentials
        logger.debug("JWT token extracted from Authorization header")
    elif token:
        jwt_token = token
        logger.debug("JWT token extracted from cookie")

    # Reject if no token provided
    if not jwt_token:
        logger.warning("Authentication failed: No token provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        # Decode and verify JWT token
        payload = jwt.decode(
            jwt_token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM],
            options={
                "verify_signature": True,
                "verify_exp": True,
                "require": ["sub", "exp"],
            },
        )

        # Extract user_id from 'sub' claim
        user_id: Optional[str] = payload.get("sub")

        if not user_id:
            logger.warning("Authentication failed: Missing 'sub' claim in token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        logger.debug(f"JWT verification successful for user_id: {user_id}")
        return user_id

    except jwt.ExpiredSignatureError:
        logger.warning("Authentication failed: Token expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    except jwt.InvalidTokenError as e:
        logger.warning(f"Authentication failed: Invalid token - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    except Exception as e:
        # Catch-all for unexpected errors (don't expose internal details)
        logger.error(f"Unexpected error during JWT verification: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )


def create_jwt_token(user_id: str, expires_in_hours: int = 24) -> str:
    """
    Create a JWT token for authenticated user.

    [Task]: T011
    [From]: specs/002-auth-jwt/plan.md §JWT Token Generation

    Args:
        user_id: Unique user identifier to encode in token
        expires_in_hours: Token validity period (default 24 hours)

    Returns:
        str: Encoded JWT token

    Note:
        This helper function is used by auth routes to generate tokens
        after successful signup/signin. The token contains:
        - sub: user_id (standard JWT claim for subject)
        - exp: expiration timestamp (Unix timestamp)
        - iat: issued at timestamp (Unix timestamp)
    """
    from datetime import timedelta

    now = datetime.utcnow()
    expiration = now + timedelta(hours=expires_in_hours)

    payload = {
        "sub": user_id,  # Subject (user identifier)
        "exp": expiration,  # Expiration time
        "iat": now,  # Issued at time
    }

    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    logger.debug(f"JWT token created for user_id: {user_id}, expires: {expiration}")

    return token
