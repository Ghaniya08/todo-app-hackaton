"""
Contract tests for Authentication API endpoints.

[Task]: T014, T015, T016, T017
[From]: specs/002-auth-jwt/contracts/auth-api.yaml
[From]: specs/002-auth-jwt/spec.md §User Story 1

These tests verify that the authentication API endpoints conform to the
OpenAPI contract specification. They test request/response formats,
status codes, error handling, and security requirements.

Test Strategy (TDD Red Phase):
- Write tests FIRST before implementation
- Tests should FAIL initially (endpoints don't exist yet)
- Tests define the contract that implementation must satisfy
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from src.models.user import User
from passlib.context import CryptContext

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)


class TestSignupEndpoint:
    """
    Contract tests for POST /api/auth/signup endpoint.

    [Task]: T014
    [From]: specs/002-auth-jwt/contracts/auth-api.yaml §/api/auth/signup
    """

    def test_signup_valid_data(self, client: TestClient, session: Session):
        """
        Test successful user signup with valid data.

        Given: Valid email, password, and name
        When: POST /api/auth/signup
        Then: Returns 201 with user details and sets JWT cookie

        [Task]: T014
        [From]: auth-api.yaml §POST /api/auth/signup - 201 response
        """
        # Arrange
        signup_data = {
            "email": "newuser@example.com",
            "password": "securepass123",
            "name": "New User"
        }

        # Act
        response = client.post("/api/auth/signup", json=signup_data)

        # Assert
        assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"

        # Verify response body
        data = response.json()
        assert "id" in data, "Response must include user id"
        assert data["email"] == signup_data["email"], "Email must match request"
        assert data["name"] == signup_data["name"], "Name must match request"
        assert "created_at" in data, "Response must include created_at timestamp"
        assert "password" not in data, "Response must NOT expose password"
        assert "password_hash" not in data, "Response must NOT expose password_hash"

        # Verify JWT cookie is set
        assert "set-cookie" in response.headers, "Response must set JWT cookie"
        cookie_header = response.headers["set-cookie"]
        assert "token=" in cookie_header, "Cookie must be named 'token'"
        assert "HttpOnly" in cookie_header, "Cookie must be HttpOnly"
        assert "SameSite=Strict" in cookie_header or "SameSite=strict" in cookie_header, "Cookie must have SameSite=Strict"
        assert "Max-Age=86400" in cookie_header, "Cookie must have 24h expiration (86400 seconds)"

        # Verify user was created in database
        user = session.query(User).filter(User.email == signup_data["email"]).first()
        assert user is not None, "User must be created in database"
        assert user.email == signup_data["email"]
        assert user.name == signup_data["name"]
        assert user.password_hash != signup_data["password"], "Password must be hashed"

    def test_signup_existing_email(self, client: TestClient, test_user: User):
        """
        Test signup with email that already exists.

        Given: Email already registered in database
        When: POST /api/auth/signup with duplicate email
        Then: Returns 409 Conflict

        [Task]: T014
        [From]: auth-api.yaml §POST /api/auth/signup - 409 response
        """
        # Arrange
        signup_data = {
            "email": test_user.email,  # Use existing user's email
            "password": "differentpass123",
            "name": "Another User"
        }

        # Act
        response = client.post("/api/auth/signup", json=signup_data)

        # Assert
        assert response.status_code == 409, f"Expected 409, got {response.status_code}: {response.text}"

        data = response.json()
        assert "detail" in data, "Error response must include detail field"
        assert "already" in data["detail"].lower() or "exists" in data["detail"].lower(), \
            "Error message should indicate email already exists"

    def test_signup_invalid_email(self, client: TestClient):
        """
        Test signup with invalid email format.

        Given: Invalid email format (not a valid email)
        When: POST /api/auth/signup
        Then: Returns 400 Bad Request

        [Task]: T014
        [From]: auth-api.yaml §POST /api/auth/signup - 400 response
        """
        # Arrange
        signup_data = {
            "email": "not-an-email",  # Invalid email format
            "password": "securepass123",
            "name": "Test User"
        }

        # Act
        response = client.post("/api/auth/signup", json=signup_data)

        # Assert
        assert response.status_code == 422 or response.status_code == 400, \
            f"Expected 400/422, got {response.status_code}: {response.text}"

        data = response.json()
        assert "detail" in data, "Error response must include detail field"

    def test_signup_short_password(self, client: TestClient):
        """
        Test signup with password shorter than 8 characters.

        Given: Password with less than 8 characters
        When: POST /api/auth/signup
        Then: Returns 400 Bad Request

        [Task]: T014
        [From]: auth-api.yaml §POST /api/auth/signup - 400 response
        """
        # Arrange
        signup_data = {
            "email": "user@example.com",
            "password": "short",  # Only 5 characters
            "name": "Test User"
        }

        # Act
        response = client.post("/api/auth/signup", json=signup_data)

        # Assert
        assert response.status_code == 422 or response.status_code == 400, \
            f"Expected 400/422, got {response.status_code}: {response.text}"

        data = response.json()
        assert "detail" in data, "Error response must include detail field"


class TestSigninEndpoint:
    """
    Contract tests for POST /api/auth/signin endpoint.

    [Task]: T015
    [From]: specs/002-auth-jwt/contracts/auth-api.yaml §/api/auth/signin
    """

    def test_signin_correct_credentials(self, client: TestClient, test_user: User):
        """
        Test successful signin with correct credentials.

        Given: Existing user with correct email and password
        When: POST /api/auth/signin
        Then: Returns 200 with user details and sets JWT cookie

        [Task]: T015
        [From]: auth-api.yaml §POST /api/auth/signin - 200 response
        """
        # Arrange
        signin_data = {
            "email": test_user.email,
            "password": "testpassword123"  # Password from conftest.py test_user fixture
        }

        # Act
        response = client.post("/api/auth/signin", json=signin_data)

        # Assert
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

        # Verify response body
        data = response.json()
        assert data["id"] == test_user.id, "User ID must match"
        assert data["email"] == test_user.email, "Email must match"
        assert data["name"] == test_user.name, "Name must match"
        assert "password" not in data, "Response must NOT expose password"
        assert "password_hash" not in data, "Response must NOT expose password_hash"

        # Verify JWT cookie is set
        assert "set-cookie" in response.headers, "Response must set JWT cookie"
        cookie_header = response.headers["set-cookie"]
        assert "token=" in cookie_header, "Cookie must be named 'token'"
        assert "HttpOnly" in cookie_header, "Cookie must be HttpOnly"

    def test_signin_wrong_password(self, client: TestClient, test_user: User):
        """
        Test signin with incorrect password.

        Given: Existing user with wrong password
        When: POST /api/auth/signin
        Then: Returns 401 Unauthorized with generic error message

        [Task]: T015
        [From]: auth-api.yaml §POST /api/auth/signin - 401 response
        [Security]: Generic error message to avoid user enumeration
        """
        # Arrange
        signin_data = {
            "email": test_user.email,
            "password": "wrongpassword"
        }

        # Act
        response = client.post("/api/auth/signin", json=signin_data)

        # Assert
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"

        data = response.json()
        assert "detail" in data, "Error response must include detail field"
        # Generic error message (don't reveal if email exists)
        assert "invalid" in data["detail"].lower(), "Error should indicate invalid credentials"

    def test_signin_nonexistent_email(self, client: TestClient):
        """
        Test signin with email that doesn't exist.

        Given: Email not registered in database
        When: POST /api/auth/signin
        Then: Returns 401 Unauthorized with generic error message

        [Task]: T015
        [From]: auth-api.yaml §POST /api/auth/signin - 401 response
        [Security]: Same error as wrong password to prevent user enumeration
        """
        # Arrange
        signin_data = {
            "email": "nonexistent@example.com",
            "password": "somepassword123"
        }

        # Act
        response = client.post("/api/auth/signin", json=signin_data)

        # Assert
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"

        data = response.json()
        assert "detail" in data, "Error response must include detail field"
        # Generic error message (don't reveal if email exists)
        assert "invalid" in data["detail"].lower(), "Error should indicate invalid credentials"

    def test_signin_missing_fields(self, client: TestClient):
        """
        Test signin with missing required fields.

        Given: Request missing email or password
        When: POST /api/auth/signin
        Then: Returns 400 Bad Request

        [Task]: T015
        [From]: auth-api.yaml §POST /api/auth/signin - 400 response
        """
        # Arrange - missing password
        signin_data = {
            "email": "user@example.com"
            # password is missing
        }

        # Act
        response = client.post("/api/auth/signin", json=signin_data)

        # Assert
        assert response.status_code == 422 or response.status_code == 400, \
            f"Expected 400/422, got {response.status_code}: {response.text}"

        data = response.json()
        assert "detail" in data, "Error response must include detail field"


class TestSignoutEndpoint:
    """
    Contract tests for POST /api/auth/signout endpoint.

    [Task]: T016
    [From]: specs/002-auth-jwt/contracts/auth-api.yaml §/api/auth/signout
    """

    def test_signout_authenticated(self, client: TestClient, test_jwt_token: str):
        """
        Test successful signout for authenticated user.

        Given: Authenticated user with valid JWT token
        When: POST /api/auth/signout
        Then: Returns 200 with success message

        [Task]: T016
        [From]: auth-api.yaml §POST /api/auth/signout - 200 response
        """
        # Arrange - set JWT token in cookie
        client.cookies.set("token", test_jwt_token)

        # Act
        response = client.post("/api/auth/signout")

        # Assert
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

        data = response.json()
        assert "message" in data, "Response must include success message"
        assert "signed out" in data["message"].lower() or "signout" in data["message"].lower(), \
            "Message should confirm signout"

    def test_signout_clears_cookie(self, client: TestClient, test_jwt_token: str):
        """
        Test that signout clears the JWT cookie.

        Given: Authenticated user
        When: POST /api/auth/signout
        Then: Response sets cookie with Max-Age=0 to clear it

        [Task]: T016
        [From]: auth-api.yaml §POST /api/auth/signout - Set-Cookie header
        """
        # Arrange
        client.cookies.set("token", test_jwt_token)

        # Act
        response = client.post("/api/auth/signout")

        # Assert
        assert response.status_code == 200

        # Verify cookie is cleared
        assert "set-cookie" in response.headers, "Response must set cookie to clear it"
        cookie_header = response.headers["set-cookie"]
        assert "token=" in cookie_header, "Cookie must be named 'token'"
        assert "Max-Age=0" in cookie_header, "Cookie must have Max-Age=0 to clear it"


class TestGetCurrentUserEndpoint:
    """
    Contract tests for GET /api/auth/me endpoint.

    [Task]: T017
    [From]: specs/002-auth-jwt/contracts/auth-api.yaml §/api/auth/me
    """

    def test_get_current_user_authenticated(self, client: TestClient, test_user: User, test_jwt_token: str):
        """
        Test getting current user info when authenticated.

        Given: Authenticated user with valid JWT token
        When: GET /api/auth/me
        Then: Returns 200 with user information

        [Task]: T017
        [From]: auth-api.yaml §GET /api/auth/me - 200 response
        """
        # Arrange - set JWT token in cookie
        client.cookies.set("token", test_jwt_token)

        # Act
        response = client.get("/api/auth/me")

        # Assert
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

        data = response.json()
        assert data["id"] == test_user.id, "User ID must match"
        assert data["email"] == test_user.email, "Email must match"
        assert data["name"] == test_user.name, "Name must match"
        assert "created_at" in data, "Response must include created_at"
        assert "password" not in data, "Response must NOT expose password"
        assert "password_hash" not in data, "Response must NOT expose password_hash"

    def test_get_current_user_unauthenticated(self, client: TestClient):
        """
        Test getting current user info without authentication.

        Given: No JWT token provided
        When: GET /api/auth/me
        Then: Returns 401 Unauthorized

        [Task]: T017
        [From]: auth-api.yaml §GET /api/auth/me - 401 response
        """
        # Arrange - no token set

        # Act
        response = client.get("/api/auth/me")

        # Assert
        assert response.status_code == 401, f"Expected 401, got {response.status_code}: {response.text}"

        data = response.json()
        assert "detail" in data, "Error response must include detail field"
