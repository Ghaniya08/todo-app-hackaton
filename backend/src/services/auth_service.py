"""
Authentication service for user signup, signin, and JWT token management.

[Task]: T019, T020, T021
[From]: specs/002-auth-jwt/plan.md §Phase 3 - Authentication Service
[From]: specs/002-auth-jwt/spec.md §User Story 1
"""

import uuid
import logging
from typing import Optional
from datetime import datetime, timedelta
from sqlmodel import Session, select
from passlib.context import CryptContext
import jwt

from ..models.user import User
from ..config import settings

logger = logging.getLogger(__name__)

# Password hashing configuration
# [Task]: T019 - Use bcrypt with cost factor 12 for security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)

# JWT configuration
JWT_ALGORITHM = "HS256"
JWT_SECRET = settings.better_auth_secret
JWT_EXPIRATION_HOURS = 24


class AuthService:
    """
    Service class for authentication operations.

    Handles user registration, password verification, and JWT token generation.
    All methods follow security best practices for authentication systems.
    """

    @staticmethod
    def create_user(
        session: Session,
        email: str,
        password: str,
        name: Optional[str] = None
    ) -> User:
        """
        Create a new user account with hashed password.

        [Task]: T019
        [From]: specs/002-auth-jwt/contracts/auth-api.yaml §POST /api/auth/signup

        Args:
            session: Database session
            email: User's email address (must be unique)
            password: User's plain text password (will be hashed)
            name: User's display name (optional)

        Returns:
            User: Created user object (without password_hash)

        Raises:
            ValueError: If email already exists in database

        Security Notes:
            - Password is hashed using bcrypt with cost factor 12
            - User ID is generated as UUID for uniqueness
            - Password hash is never exposed in return value
        """
        # [Task]: T019 - Validate email uniqueness
        existing_user = session.exec(
            select(User).where(User.email == email)
        ).first()

        if existing_user:
            logger.warning(f"Signup attempt with existing email: {email}")
            raise ValueError("Email already registered")

        # [Task]: T019 - Hash password with bcrypt cost factor 12
        password_hash = pwd_context.hash(password)

        # [Task]: T019 - Generate UUID for user_id
        user_id = str(uuid.uuid4())

        # [Task]: T019 - Create user record in database
        user = User(
            id=user_id,
            email=email,
            password_hash=password_hash,
            name=name,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        session.add(user)
        session.commit()
        session.refresh(user)

        logger.info(f"User created successfully: {user_id} ({email})")

        # [Task]: T019 - Return User object (password_hash excluded by response schema)
        return user

    @staticmethod
    def verify_password(session: Session, email: str, password: str) -> Optional[User]:
        """
        Verify user credentials and return user if valid.

        [Task]: T020
        [From]: specs/002-auth-jwt/contracts/auth-api.yaml §POST /api/auth/signin

        Args:
            session: Database session
            email: User's email address
            password: User's plain text password

        Returns:
            User: User object if credentials are valid, None otherwise

        Security Notes:
            - Uses constant-time comparison via bcrypt.verify
            - Returns None for both "user not found" and "wrong password"
              to prevent user enumeration attacks
            - Logs authentication attempts without exposing sensitive data
        """
        # [Task]: T020 - Lookup user by email
        user = session.exec(
            select(User).where(User.email == email)
        ).first()

        if not user:
            logger.warning(f"Signin attempt with non-existent email: {email}")
            return None

        # [Task]: T020 - Verify password hash using bcrypt
        if not pwd_context.verify(password, user.password_hash):
            logger.warning(f"Signin attempt with incorrect password for email: {email}")
            return None

        logger.info(f"User authenticated successfully: {user.id} ({email})")

        # [Task]: T020 - Return user object if valid
        return user

    @staticmethod
    def generate_jwt(user_id: str, email: str, expires_in_hours: int = JWT_EXPIRATION_HOURS) -> str:
        """
        Generate JWT token for authenticated user.

        [Task]: T021
        [From]: specs/002-auth-jwt/plan.md §JWT Token Generation
        [From]: specs/002-auth-jwt/contracts/auth-api.yaml §Security Schemes

        Args:
            user_id: Unique user identifier
            email: User's email address
            expires_in_hours: Token validity period (default 24 hours)

        Returns:
            str: Encoded JWT token

        Token Payload:
            - sub: user_id (standard JWT claim for subject)
            - email: user's email address
            - iat: issued at timestamp (Unix timestamp)
            - exp: expiration timestamp (Unix timestamp)

        Security Notes:
            - Token signed with BETTER_AUTH_SECRET using HS256 algorithm
            - Expiration set to 24 hours (industry standard for web apps)
            - Token contains minimal user information (no sensitive data)
        """
        # [Task]: T021 - Create JWT payload with required claims
        now = datetime.utcnow()
        expiration = now + timedelta(hours=expires_in_hours)

        payload = {
            "sub": user_id,  # Subject (user identifier) - standard JWT claim
            "email": email,  # User's email for convenience
            "iat": now,  # Issued at time
            "exp": expiration,  # Expiration time
        }

        # [Task]: T021 - Sign with BETTER_AUTH_SECRET using HS256
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

        logger.debug(f"JWT token generated for user_id: {user_id}, expires: {expiration}")

        return token
