"""
Integration tests for user stories.

[Task]: T016, T018, T028, T035
[From]: specs/001-backend-task-api/spec.md §User Scenarios & Testing
[From]: specs/002-auth-jwt/spec.md §User Scenarios & Testing

These tests verify complete user journeys across multiple endpoints.
Tests are written FIRST (TDD red phase) before implementation.
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session


class TestUserStory1:
    """Integration tests for User Story 1 - Create and View Tasks."""

    def test_user_story_1_create_and_view(self, client: TestClient):
        """
        Test complete user journey for User Story 1.

        Scenario:
        1. User creates a new task with title and description
        2. User retrieves the task list and sees the new task
        3. User retrieves the specific task by ID
        4. User verifies data isolation (cannot see other users' tasks)
        """
        # Step 1: Create a new task
        create_response = client.post(
            "/api/user123/tasks",
            json={
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
            },
        )
        assert create_response.status_code == 201
        created_task = create_response.json()
        task_id = created_task["id"]
        assert created_task["title"] == "Buy groceries"
        assert created_task["description"] == "Milk, eggs, bread"
        assert created_task["user_id"] == "user123"
        assert created_task["completed"] is False

        # Step 2: Retrieve task list
        list_response = client.get("/api/user123/tasks")
        assert list_response.status_code == 200
        tasks = list_response.json()
        assert len(tasks) >= 1
        assert any(task["id"] == task_id for task in tasks)

        # Step 3: Retrieve specific task by ID
        get_response = client.get(f"/api/user123/tasks/{task_id}")
        assert get_response.status_code == 200
        retrieved_task = get_response.json()
        assert retrieved_task["id"] == task_id
        assert retrieved_task["title"] == "Buy groceries"
        assert retrieved_task["description"] == "Milk, eggs, bread"

        # Step 4: Verify data isolation
        # Create a task for another user
        client.post(
            "/api/user456/tasks",
            json={"title": "User456 Task"},
        )

        # Verify user123 cannot see user456's tasks
        user123_tasks = client.get("/api/user123/tasks").json()
        for task in user123_tasks:
            assert task["user_id"] == "user123"

        # Verify user456 cannot see user123's tasks
        user456_tasks = client.get("/api/user456/tasks").json()
        for task in user456_tasks:
            assert task["user_id"] == "user456"

    def test_user_story_1_multiple_tasks(self, client: TestClient):
        """
        Test creating and viewing multiple tasks.

        Scenario:
        1. User creates 3 tasks
        2. User retrieves task list and sees all 3 tasks
        3. User retrieves each task individually
        """
        # Create 3 tasks
        task_ids = []
        for i in range(1, 4):
            response = client.post(
                "/api/user123/tasks",
                json={
                    "title": f"Task {i}",
                    "description": f"Description {i}",
                },
            )
            assert response.status_code == 201
            task_ids.append(response.json()["id"])

        # Retrieve task list
        list_response = client.get("/api/user123/tasks")
        assert list_response.status_code == 200
        tasks = list_response.json()
        assert len(tasks) == 3

        # Retrieve each task individually
        for task_id in task_ids:
            response = client.get(f"/api/user123/tasks/{task_id}")
            assert response.status_code == 200
            task = response.json()
            assert task["id"] == task_id
            assert task["user_id"] == "user123"


class TestUserStory2:
    """Integration tests for User Story 2 - Update and Delete Tasks."""

    def test_user_story_2_update_and_delete(self, client: TestClient):
        """
        Test complete user journey for User Story 2.

        Scenario:
        1. User creates a task
        2. User updates the task's title and description
        3. User verifies the changes
        4. User deletes the task
        5. User verifies the task is gone
        """
        # Step 1: Create a task
        create_response = client.post(
            "/api/user123/tasks",
            json={
                "title": "Original Title",
                "description": "Original Description",
            },
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["id"]

        # Step 2: Update the task
        update_response = client.put(
            f"/api/user123/tasks/{task_id}",
            json={
                "title": "Updated Title",
                "description": "Updated Description",
            },
        )
        assert update_response.status_code == 200
        updated_task = update_response.json()
        assert updated_task["id"] == task_id
        assert updated_task["title"] == "Updated Title"
        assert updated_task["description"] == "Updated Description"

        # Step 3: Verify the changes
        get_response = client.get(f"/api/user123/tasks/{task_id}")
        assert get_response.status_code == 200
        retrieved_task = get_response.json()
        assert retrieved_task["title"] == "Updated Title"
        assert retrieved_task["description"] == "Updated Description"

        # Step 4: Delete the task
        delete_response = client.delete(f"/api/user123/tasks/{task_id}")
        assert delete_response.status_code == 204

        # Step 5: Verify the task is gone
        get_after_delete = client.get(f"/api/user123/tasks/{task_id}")
        assert get_after_delete.status_code == 404

    def test_user_story_2_ownership_validation(self, client: TestClient):
        """
        Test that users cannot update or delete other users' tasks.

        Scenario:
        1. User A creates a task
        2. User B tries to update User A's task (should fail)
        3. User B tries to delete User A's task (should fail)
        4. User A's task remains unchanged
        """
        # Step 1: User A creates a task
        create_response = client.post(
            "/api/userA/tasks",
            json={"title": "User A Task"},
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["id"]

        # Step 2: User B tries to update User A's task
        update_response = client.put(
            f"/api/userB/tasks/{task_id}",
            json={"title": "Hacked Title"},
        )
        assert update_response.status_code == 404

        # Step 3: User B tries to delete User A's task
        delete_response = client.delete(f"/api/userB/tasks/{task_id}")
        assert delete_response.status_code == 404

        # Step 4: Verify User A's task remains unchanged
        get_response = client.get(f"/api/userA/tasks/{task_id}")
        assert get_response.status_code == 200
        task = get_response.json()
        assert task["title"] == "User A Task"


class TestUserStory3:
    """Integration tests for User Story 3 - Mark Tasks Complete."""

    def test_user_story_3_mark_complete(self, client: TestClient):
        """
        Test complete user journey for User Story 3.

        Scenario:
        1. User creates a task (default: incomplete)
        2. User marks the task as complete
        3. User verifies the task is complete
        4. User marks the task as incomplete again
        5. User verifies the task is incomplete
        """
        # Step 1: Create a task
        create_response = client.post(
            "/api/user123/tasks",
            json={"title": "Task to Complete"},
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["id"]
        assert create_response.json()["completed"] is False

        # Step 2: Mark the task as complete
        complete_response = client.patch(f"/api/user123/tasks/{task_id}/complete")
        assert complete_response.status_code == 200
        assert complete_response.json()["completed"] is True

        # Step 3: Verify the task is complete
        get_response = client.get(f"/api/user123/tasks/{task_id}")
        assert get_response.status_code == 200
        assert get_response.json()["completed"] is True

        # Step 4: Mark the task as incomplete again
        incomplete_response = client.patch(f"/api/user123/tasks/{task_id}/complete")
        assert incomplete_response.status_code == 200
        assert incomplete_response.json()["completed"] is False

        # Step 5: Verify the task is incomplete
        get_response = client.get(f"/api/user123/tasks/{task_id}")
        assert get_response.status_code == 200
        assert get_response.json()["completed"] is False

    def test_user_story_3_completion_ownership(self, client: TestClient):
        """
        Test that users cannot complete other users' tasks.

        Scenario:
        1. User A creates a task
        2. User B tries to complete User A's task (should fail)
        3. User A's task remains incomplete
        """
        # Step 1: User A creates a task
        create_response = client.post(
            "/api/userA/tasks",
            json={"title": "User A Task"},
        )
        assert create_response.status_code == 201
        task_id = create_response.json()["id"]

        # Step 2: User B tries to complete User A's task
        complete_response = client.patch(f"/api/userB/tasks/{task_id}/complete")
        assert complete_response.status_code == 404

        # Step 3: Verify User A's task remains incomplete
        get_response = client.get(f"/api/userA/tasks/{task_id}")
        assert get_response.status_code == 200
        assert get_response.json()["completed"] is False


class TestAuthUserStory1:
    """
    Integration tests for Authentication User Story 1 - User Registration and Sign-In.

    [Task]: T018
    [From]: specs/002-auth-jwt/spec.md §User Story 1
    """

    def test_user_story_1_signup_and_signin(self, client: TestClient, session: Session):
        """
        Test complete user journey for Authentication User Story 1.

        Scenario:
        1. New user signs up with valid credentials
        2. User receives JWT token and is authenticated
        3. User signs out (clears session)
        4. User signs in with correct credentials
        5. User receives new JWT token and is authenticated
        6. User can access protected endpoint (GET /api/auth/me)

        [Task]: T018
        [From]: specs/002-auth-jwt/spec.md §User Story 1 - Acceptance Scenarios
        """
        # Step 1: New user signs up
        signup_data = {
            "email": "journey@example.com",
            "password": "securepass123",
            "name": "Journey User"
        }
        signup_response = client.post("/api/auth/signup", json=signup_data)
        assert signup_response.status_code == 201, f"Signup failed: {signup_response.text}"

        # Verify user details returned
        user_data = signup_response.json()
        assert user_data["email"] == signup_data["email"]
        assert user_data["name"] == signup_data["name"]
        assert "id" in user_data
        user_id = user_data["id"]

        # Step 2: Verify JWT token is set in cookie
        assert "set-cookie" in signup_response.headers
        cookie_header = signup_response.headers["set-cookie"]
        assert "token=" in cookie_header
        assert "HttpOnly" in cookie_header

        # Extract token from cookie for subsequent requests
        # TestClient should automatically handle cookies, but we'll verify explicitly
        token_start = cookie_header.find("token=") + 6
        token_end = cookie_header.find(";", token_start)
        jwt_token = cookie_header[token_start:token_end]
        assert len(jwt_token) > 0, "JWT token should not be empty"

        # Step 3: Verify user can access protected endpoint
        client.cookies.set("token", jwt_token)
        me_response = client.get("/api/auth/me")
        assert me_response.status_code == 200, f"GET /api/auth/me failed: {me_response.text}"
        me_data = me_response.json()
        assert me_data["id"] == user_id
        assert me_data["email"] == signup_data["email"]

        # Step 4: User signs out
        signout_response = client.post("/api/auth/signout")
        assert signout_response.status_code == 200, f"Signout failed: {signout_response.text}"

        # Verify cookie is cleared
        assert "set-cookie" in signout_response.headers
        signout_cookie = signout_response.headers["set-cookie"]
        assert "Max-Age=0" in signout_cookie, "Cookie should be cleared with Max-Age=0"

        # Clear the cookie from client
        client.cookies.clear()

        # Step 5: Verify user cannot access protected endpoint after signout
        me_after_signout = client.get("/api/auth/me")
        assert me_after_signout.status_code == 401, "Should be unauthorized after signout"

        # Step 6: User signs in with correct credentials
        signin_data = {
            "email": signup_data["email"],
            "password": signup_data["password"]
        }
        signin_response = client.post("/api/auth/signin", json=signin_data)
        assert signin_response.status_code == 200, f"Signin failed: {signin_response.text}"

        # Verify user details returned
        signin_user_data = signin_response.json()
        assert signin_user_data["id"] == user_id
        assert signin_user_data["email"] == signup_data["email"]

        # Step 7: Verify new JWT token is set
        assert "set-cookie" in signin_response.headers
        signin_cookie = signin_response.headers["set-cookie"]
        assert "token=" in signin_cookie
        assert "HttpOnly" in signin_cookie

        # Extract new token
        token_start = signin_cookie.find("token=") + 6
        token_end = signin_cookie.find(";", token_start)
        new_jwt_token = signin_cookie[token_start:token_end]
        assert len(new_jwt_token) > 0

        # Step 8: Verify user can access protected endpoint with new token
        client.cookies.set("token", new_jwt_token)
        me_after_signin = client.get("/api/auth/me")
        assert me_after_signin.status_code == 200, f"GET /api/auth/me after signin failed: {me_after_signin.text}"
        me_after_signin_data = me_after_signin.json()
        assert me_after_signin_data["id"] == user_id
        assert me_after_signin_data["email"] == signup_data["email"]

    def test_user_story_1_invalid_credentials(self, client: TestClient):
        """
        Test authentication failure scenarios.

        Scenario:
        1. User tries to sign in with non-existent email
        2. User signs up successfully
        3. User tries to sign in with wrong password
        4. All attempts return 401 with generic error message

        [Task]: T018
        [From]: specs/002-auth-jwt/spec.md §User Story 1 - Acceptance Scenarios
        """
        # Step 1: Try to sign in with non-existent email
        signin_data = {
            "email": "nonexistent@example.com",
            "password": "somepassword123"
        }
        signin_response = client.post("/api/auth/signin", json=signin_data)
        assert signin_response.status_code == 401
        assert "invalid" in signin_response.json()["detail"].lower()

        # Step 2: Sign up successfully
        signup_data = {
            "email": "testfail@example.com",
            "password": "correctpass123",
            "name": "Test Fail User"
        }
        signup_response = client.post("/api/auth/signup", json=signup_data)
        assert signup_response.status_code == 201

        # Step 3: Try to sign in with wrong password
        wrong_password_data = {
            "email": signup_data["email"],
            "password": "wrongpassword"
        }
        wrong_pass_response = client.post("/api/auth/signin", json=wrong_password_data)
        assert wrong_pass_response.status_code == 401
        assert "invalid" in wrong_pass_response.json()["detail"].lower()

    def test_user_story_1_duplicate_email(self, client: TestClient):
        """
        Test that duplicate email registration is prevented.

        Scenario:
        1. User signs up with email
        2. Another user tries to sign up with same email
        3. Second signup returns 409 Conflict

        [Task]: T018
        [From]: specs/002-auth-jwt/spec.md §User Story 1 - Acceptance Scenarios
        """
        # Step 1: First user signs up
        signup_data = {
            "email": "duplicate@example.com",
            "password": "password123",
            "name": "First User"
        }
        first_signup = client.post("/api/auth/signup", json=signup_data)
        assert first_signup.status_code == 201

        # Step 2: Second user tries to sign up with same email
        duplicate_data = {
            "email": "duplicate@example.com",  # Same email
            "password": "differentpass456",
            "name": "Second User"
        }
        duplicate_signup = client.post("/api/auth/signup", json=duplicate_data)
        assert duplicate_signup.status_code == 409
        assert "already" in duplicate_signup.json()["detail"].lower() or \
               "exists" in duplicate_signup.json()["detail"].lower()
