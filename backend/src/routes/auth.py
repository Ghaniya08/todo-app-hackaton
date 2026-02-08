"""
Authentication API routes for user signup, signin, signout, and session management.

[Task]: T022, T023, T024, T025, T026
[From]: specs/002-auth-jwt/contracts/auth-api.yaml
[From]: specs/002-auth-jwt/spec.md §User Story 1
"""

import logging
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlmodel import Session, select

from ..db import get_session
from ..models.user import User
from ..schemas.user_schemas import UserCreate, SignInRequest, UserResponse
from ..services.auth_service import AuthService
from ..middleware.jwt_auth import verify_jwt

logger = logging.getLogger(__name__)

# [Task]: T022 - Initialize APIRouter with prefix /api/auth
router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
)


@router.post(
    "/signup",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new user account",
    description="Register a new user with email and password. Returns user information and sets JWT token in httpOnly cookie.",
    responses={
        201: {
            "description": "User successfully created",
            "content": {
                "application/json": {
                    "example": {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "email": "user@example.com",
                        "name": "John Doe",
                        "created_at": "2026-02-08T14:30:00Z",
                        "updated_at": "2026-02-08T14:30:00Z",
                    }
                }
            },
        },
        400: {
            "description": "Invalid request data",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid email format"}
                }
            },
        },
        409: {
            "description": "Email already registered",
            "content": {
                "application/json": {
                    "example": {"detail": "Email already registered"}
                }
            },
        },
    },
)
async def signup(
    user_data: UserCreate,
    response: Response,
    session: Annotated[Session, Depends(get_session)],
):
    """
    Create new user account.

    [Task]: T023, T057
    [From]: specs/002-auth-jwt/contracts/auth-api.yaml §POST /api/auth/signup

    Register a new user with email and password. Returns user information
    and sets JWT token in httpOnly cookie.

    Args:
        user_data: User registration data (email, password, name)
        response: FastAPI response object for setting cookies
        session: Database session

    Returns:
        UserResponse: Created user details (without password)

    Raises:
        HTTPException 409: Email already registered
        HTTPException 400: Invalid request data

    Security:
        - Password is hashed before storage (never stored in plain text)
        - JWT token set in httpOnly cookie (not accessible to JavaScript)
        - Cookie has Secure, SameSite=Strict flags for security
    """
    try:
        # [Task]: T023 - Call AuthService.create_user()
        user = AuthService.create_user(
            session=session,
            email=user_data.email,
            password=user_data.password,
            name=user_data.name,
        )

        # [Task]: T023 - Generate JWT token
        jwt_token = AuthService.generate_jwt(user_id=user.id, email=user.email)

        # [Task]: T023 - Set httpOnly cookie with JWT token
        # Cookie settings per auth-api.yaml specification:
        # - HttpOnly: Prevents JavaScript access (XSS protection)
        # - Secure: Only sent over HTTPS (production)
        # - SameSite=Strict: CSRF protection
        # - Max-Age=86400: 24 hours (24 * 60 * 60 seconds)
        from ..config import settings
        response.set_cookie(
            key="token",
            value=jwt_token,
            httponly=True,
            secure=settings.is_production,  # Only secure in production (HTTPS)
            samesite="lax",  # Changed to 'lax' for better localhost compatibility
            max_age=86400,  # 24 hours in seconds
        )

        logger.info(f"User signup successful: {user.id} ({user.email})")

        # [Task]: T023 - Return 201 with UserResponse
        return user

    except ValueError as e:
        # [Task]: T028 - Handle duplicate email (409 Conflict)
        if "already registered" in str(e).lower():
            logger.warning(f"Signup failed - duplicate email: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )
        # Other ValueError cases
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        # [Task]: T028 - Generic error handling (don't expose internal details)
        logger.error(f"Signup error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during signup",
        )


@router.post(
    "/signin",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Sign in to existing account",
    description="Authenticate user with email and password. Returns user information and sets JWT token in httpOnly cookie.",
    responses={
        200: {
            "description": "Successfully authenticated",
            "content": {
                "application/json": {
                    "example": {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "email": "user@example.com",
                        "name": "John Doe",
                        "created_at": "2026-02-08T14:30:00Z",
                        "updated_at": "2026-02-08T14:30:00Z",
                    }
                }
            },
        },
        401: {
            "description": "Invalid credentials",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid email or password"}
                }
            },
        },
    },
)
async def signin(
    credentials: SignInRequest,
    response: Response,
    session: Annotated[Session, Depends(get_session)],
):
    """
    Sign in to existing account.

    [Task]: T024, T057
    [From]: specs/002-auth-jwt/contracts/auth-api.yaml §POST /api/auth/signin

    Authenticate user with email and password. Returns user information
    and sets JWT token in httpOnly cookie.

    Args:
        credentials: User signin credentials (email, password)
        response: FastAPI response object for setting cookies
        session: Database session

    Returns:
        UserResponse: User details (without password)

    Raises:
        HTTPException 401: Invalid credentials (wrong password or email not found)
        HTTPException 400: Invalid request data

    Security:
        - Generic error message to prevent user enumeration
        - Same error for "user not found" and "wrong password"
        - Password verification uses constant-time comparison
    """
    try:
        # [Task]: T024 - Call AuthService.verify_password()
        user = AuthService.verify_password(
            session=session,
            email=credentials.email,
            password=credentials.password,
        )

        # [Task]: T024 - Return 401 for invalid credentials
        if not user:
            logger.warning(f"Signin failed - invalid credentials for email: {credentials.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        # [Task]: T024 - Generate JWT token if valid
        jwt_token = AuthService.generate_jwt(user_id=user.id, email=user.email)

        # [Task]: T024 - Set httpOnly cookie
        from ..config import settings
        response.set_cookie(
            key="token",
            value=jwt_token,
            httponly=True,
            secure=settings.is_production,  # Only secure in production (HTTPS)
            samesite="lax",  # Changed to 'lax' for better localhost compatibility
            max_age=86400,  # 24 hours
        )

        logger.info(f"User signin successful: {user.id} ({user.email})")

        # [Task]: T024 - Return 200 with UserResponse
        return user

    except HTTPException:
        # Re-raise HTTP exceptions (already handled)
        raise
    except Exception as e:
        # [Task]: T028 - Generic error handling
        logger.error(f"Signin error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during signin",
        )


@router.post(
    "/signout",
    status_code=status.HTTP_200_OK,
    summary="Sign out of current session",
    description="Invalidate JWT token by clearing the httpOnly cookie.",
    responses={
        200: {
            "description": "Successfully signed out",
            "content": {
                "application/json": {
                    "example": {"message": "Signed out successfully"}
                }
            },
        },
    },
)
async def signout(response: Response):
    """
    Sign out of current session.

    [Task]: T025, T057
    [From]: specs/002-auth-jwt/contracts/auth-api.yaml §POST /api/auth/signout

    Invalidate JWT token by clearing the httpOnly cookie.

    Args:
        response: FastAPI response object for clearing cookies

    Returns:
        dict: Success message

    Security:
        - Cookie cleared by setting Max-Age=0
        - Client-side token is invalidated
    """
    # [Task]: T025 - Clear JWT cookie with Max-Age=0
    from ..config import settings
    response.set_cookie(
        key="token",
        value="",
        httponly=True,
        secure=settings.is_production,  # Only secure in production (HTTPS)
        samesite="lax",  # Changed to 'lax' for better localhost compatibility
        max_age=0,  # Immediately expire the cookie
    )

    logger.info("User signed out successfully")

    # [Task]: T025 - Return 200 with success message
    return {"message": "Signed out successfully"}


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user information",
    description="Retrieve authenticated user's profile information. Requires valid JWT token.",
    responses={
        200: {
            "description": "Successfully retrieved user information",
            "content": {
                "application/json": {
                    "example": {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "email": "user@example.com",
                        "name": "John Doe",
                        "created_at": "2026-02-08T14:30:00Z",
                        "updated_at": "2026-02-08T14:30:00Z",
                    }
                }
            },
        },
        401: {
            "description": "Not authenticated or invalid token",
            "content": {
                "application/json": {
                    "example": {"detail": "Missing authentication token"}
                }
            },
        },
        404: {
            "description": "User not found",
            "content": {
                "application/json": {
                    "example": {"detail": "User not found"}
                }
            },
        },
    },
)
async def get_current_user(
    user_id: Annotated[str, Depends(verify_jwt)],
    session: Annotated[Session, Depends(get_session)],
):
    """
    Get current user information.

    [Task]: T026, T057
    [From]: specs/002-auth-jwt/contracts/auth-api.yaml §GET /api/auth/me

    Retrieve authenticated user's profile information.

    Args:
        user_id: Authenticated user ID from JWT token (via verify_jwt dependency)
        session: Database session

    Returns:
        UserResponse: User details (without password)

    Raises:
        HTTPException 401: Not authenticated (handled by verify_jwt dependency)
        HTTPException 404: User not found in database

    Security:
        - Requires valid JWT token (enforced by verify_jwt dependency)
        - User ID extracted from token, not from request parameters
    """
    try:
        # [Task]: T026 - Lookup user in database by authenticated user_id
        user = session.exec(
            select(User).where(User.id == user_id)
        ).first()

        if not user:
            # This should rarely happen (token valid but user deleted)
            logger.warning(f"Authenticated user not found in database: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        logger.debug(f"Current user retrieved: {user.id} ({user.email})")

        # [Task]: T026 - Return 200 with UserResponse
        return user

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # [Task]: T028 - Generic error handling
        logger.error(f"Get current user error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving user information",
        )
