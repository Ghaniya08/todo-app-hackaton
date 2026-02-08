"""
Unit tests for AuthService.

[Task]: T056
[From]: specs/002-auth-jwt/plan.md §Phase 3 - Authentication Service
[From]: specs/002-auth-jwt/spec.md §User Story 1
"""

import pytest
import jwt
from datetime import datetime, timedelta
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool

from src.models.user import User
from src.services.auth_service import AuthService, pwd_context, JWT_SECRET, JWT_ALGORITHM


@pytest.fixture(name="session")
def session_fixture():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


class TestAuthServiceCreateUser:
    """Test suite for AuthService.create_user()."""

    def test_create_user_success(self, session: Session):
        """Test successful user creation with valid data."""
        # Arrange
        email = "test@example.com"
        password = "SecurePassword123!"
        name = "Test User"

        # Act
        user = AuthService.create_user(session, email, password, name)

        # Assert
        assert user.id is not None
        assert user.email == email
        assert user.name == name
        assert user.password_hash is not None
        assert user.password_hash != password  # Password should be hashed
        assert user.created_at is not None
        assert user.updated_at is not None

        # Verify password hash is valid bcrypt hash
        assert pwd_context.verify(password, user.password_hash)

    def test_create_user_hashes_password(self, session: Session):
        """Test that password is properly hashed using bcrypt."""
        # Arrange
        email = "hash@example.com"
        password = "MyPassword123"

        # Act
        user = AuthService.create_user(session, email, password)

        # Assert
        # Password should be hashed (bcrypt hashes start with $2b$)
        assert user.password_hash.startswith("$2b$")
        # Password hash should be different from plain password
        assert user.password_hash != password
        # Should be able to verify the password
        assert pwd_context.verify(password, user.password_hash)

    def test_create_user_without_name(self, session: Session):
        """Test user creation without optional name field."""
        # Arrange
        email = "noname@example.com"
        password = "Password123"

        # Act
        user = AuthService.create_user(session, email, password, name=None)

        # Assert
        assert user.id is not None
        assert user.email == email
        assert user.name is None
        assert user.password_hash is not None

    def test_create_user_duplicate_email(self, session: Session):
        """Test that creating user with duplicate email raises ValueError."""
        # Arrange
        email = "duplicate@example.com"
        password = "Password123"

        # Create first user
        AuthService.create_user(session, email, password)

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            AuthService.create_user(session, email, "DifferentPassword")

        assert "already registered" in str(exc_info.value).lower()

    def test_create_user_generates_unique_ids(self, session: Session):
        """Test that each user gets a unique UUID."""
        # Arrange & Act
        user1 = AuthService.create_user(session, "user1@example.com", "pass1")
        user2 = AuthService.create_user(session, "user2@example.com", "pass2")

        # Assert
        assert user1.id != user2.id
        # UUIDs should be strings
        assert isinstance(user1.id, str)
        assert isinstance(user2.id, str)
        # UUIDs should have proper format (with hyphens)
        assert len(user1.id) == 36
        assert user1.id.count("-") == 4

    def test_create_user_different_passwords_different_hashes(self, session: Session):
        """Test that same password for different users produces different hashes (salt)."""
        # Arrange
        password = "SamePassword123"

        # Act
        user1 = AuthService.create_user(session, "user1@example.com", password)
        user2 = AuthService.create_user(session, "user2@example.com", password)

        # Assert
        # Even with same password, hashes should be different due to salt
        assert user1.password_hash != user2.password_hash
        # But both should verify correctly
        assert pwd_context.verify(password, user1.password_hash)
        assert pwd_context.verify(password, user2.password_hash)


class TestAuthServiceVerifyPassword:
    """Test suite for AuthService.verify_password()."""

    def test_verify_password_correct(self, session: Session):
        """Test password verification with correct credentials."""
        # Arrange
        email = "verify@example.com"
        password = "CorrectPassword123"
        AuthService.create_user(session, email, password)

        # Act
        user = AuthService.verify_password(session, email, password)

        # Assert
        assert user is not None
        assert user.email == email

    def test_verify_password_incorrect(self, session: Session):
        """Test password verification with incorrect password."""
        # Arrange
        email = "wrong@example.com"
        correct_password = "CorrectPassword123"
        wrong_password = "WrongPassword456"
        AuthService.create_user(session, email, correct_password)

        # Act
        user = AuthService.verify_password(session, email, wrong_password)

        # Assert
        assert user is None

    def test_verify_password_nonexistent_email(self, session: Session):
        """Test password verification with non-existent email."""
        # Arrange
        email = "nonexistent@example.com"
        password = "AnyPassword123"

        # Act
        user = AuthService.verify_password(session, email, password)

        # Assert
        assert user is None

    def test_verify_password_case_sensitive_email(self, session: Session):
        """Test that email comparison is case-sensitive."""
        # Arrange
        email = "CaseSensitive@example.com"
        password = "Password123"
        AuthService.create_user(session, email, password)

        # Act
        user_lowercase = AuthService.verify_password(session, email.lower(), password)

        # Assert
        # Should not find user with different case
        assert user_lowercase is None

    def test_verify_password_empty_password(self, session: Session):
        """Test password verification with empty password."""
        # Arrange
        email = "empty@example.com"
        password = "RealPassword123"
        AuthService.create_user(session, email, password)

        # Act
        user = AuthService.verify_password(session, email, "")

        # Assert
        assert user is None

    def test_verify_password_returns_user_object(self, session: Session):
        """Test that verify_password returns complete user object."""
        # Arrange
        email = "complete@example.com"
        password = "Password123"
        name = "Complete User"
        created_user = AuthService.create_user(session, email, password, name)

        # Act
        verified_user = AuthService.verify_password(session, email, password)

        # Assert
        assert verified_user is not None
        assert verified_user.id == created_user.id
        assert verified_user.email == created_user.email
        assert verified_user.name == created_user.name
        assert verified_user.password_hash == created_user.password_hash


class TestAuthServiceGenerateJWT:
    """Test suite for AuthService.generate_jwt()."""

    def test_generate_jwt_payload(self):
        """Test JWT token contains correct payload."""
        # Arrange
        user_id = "test-user-123"
        email = "test@example.com"

        # Act
        token = AuthService.generate_jwt(user_id, email)

        # Assert
        # Decode token without verification to inspect payload
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

        assert payload["sub"] == user_id
        assert payload["email"] == email
        assert "iat" in payload
        assert "exp" in payload

    def test_generate_jwt_expiration(self):
        """Test JWT token has correct expiration time."""
        # Arrange
        user_id = "test-user-456"
        email = "test@example.com"
        expires_in_hours = 24

        # Act
        token = AuthService.generate_jwt(user_id, email, expires_in_hours)

        # Assert
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

        iat = datetime.fromtimestamp(payload["iat"])
        exp = datetime.fromtimestamp(payload["exp"])

        # Expiration should be approximately 24 hours after issued time
        time_diff = exp - iat
        assert 23.9 * 3600 <= time_diff.total_seconds() <= 24.1 * 3600

    def test_generate_jwt_custom_expiration(self):
        """Test JWT token with custom expiration time."""
        # Arrange
        user_id = "test-user-789"
        email = "test@example.com"
        expires_in_hours = 1  # 1 hour

        # Act
        token = AuthService.generate_jwt(user_id, email, expires_in_hours)

        # Assert
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

        iat = datetime.fromtimestamp(payload["iat"])
        exp = datetime.fromtimestamp(payload["exp"])

        time_diff = exp - iat
        assert 0.9 * 3600 <= time_diff.total_seconds() <= 1.1 * 3600

    def test_generate_jwt_valid_signature(self):
        """Test JWT token has valid signature."""
        # Arrange
        user_id = "test-user-abc"
        email = "test@example.com"

        # Act
        token = AuthService.generate_jwt(user_id, email)

        # Assert
        # This should not raise an exception if signature is valid
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM],
            options={"verify_signature": True}
        )

        assert payload["sub"] == user_id

    def test_generate_jwt_different_users_different_tokens(self):
        """Test that different users get different tokens."""
        # Arrange
        user1_id = "user-1"
        user2_id = "user-2"
        email1 = "user1@example.com"
        email2 = "user2@example.com"

        # Act
        token1 = AuthService.generate_jwt(user1_id, email1)
        token2 = AuthService.generate_jwt(user2_id, email2)

        # Assert
        assert token1 != token2

        payload1 = jwt.decode(token1, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        payload2 = jwt.decode(token2, JWT_SECRET, algorithms=[JWT_ALGORITHM])

        assert payload1["sub"] == user1_id
        assert payload2["sub"] == user2_id

    def test_generate_jwt_token_is_string(self):
        """Test that generated token is a string."""
        # Arrange
        user_id = "test-user"
        email = "test@example.com"

        # Act
        token = AuthService.generate_jwt(user_id, email)

        # Assert
        assert isinstance(token, str)
        assert len(token) > 0

    def test_generate_jwt_with_special_characters(self):
        """Test JWT generation with special characters in user_id and email."""
        # Arrange
        user_id = "user-123_abc@domain"
        email = "test+tag@example.com"

        # Act
        token = AuthService.generate_jwt(user_id, email)

        # Assert
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        assert payload["sub"] == user_id
        assert payload["email"] == email


class TestAuthServiceIntegration:
    """Integration tests for complete authentication flow."""

    def test_signup_and_signin_flow(self, session: Session):
        """Test complete signup and signin flow."""
        # Arrange
        email = "flow@example.com"
        password = "FlowPassword123"
        name = "Flow User"

        # Act - Signup
        created_user = AuthService.create_user(session, email, password, name)
        signup_token = AuthService.generate_jwt(created_user.id, created_user.email)

        # Act - Signin
        verified_user = AuthService.verify_password(session, email, password)
        signin_token = AuthService.generate_jwt(verified_user.id, verified_user.email)

        # Assert
        assert created_user.id == verified_user.id
        assert created_user.email == verified_user.email

        # Decode both tokens
        signup_payload = jwt.decode(signup_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        signin_payload = jwt.decode(signin_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

        assert signup_payload["sub"] == signin_payload["sub"]
        assert signup_payload["email"] == signin_payload["email"]

    def test_password_change_invalidates_old_verification(self, session: Session):
        """Test that changing password invalidates old password."""
        # Arrange
        email = "change@example.com"
        old_password = "OldPassword123"
        new_password = "NewPassword456"

        user = AuthService.create_user(session, email, old_password)

        # Act - Change password (simulate by updating hash)
        new_hash = pwd_context.hash(new_password)
        user.password_hash = new_hash
        session.add(user)
        session.commit()

        # Assert
        # Old password should not work
        old_verify = AuthService.verify_password(session, email, old_password)
        assert old_verify is None

        # New password should work
        new_verify = AuthService.verify_password(session, email, new_password)
        assert new_verify is not None
        assert new_verify.id == user.id
