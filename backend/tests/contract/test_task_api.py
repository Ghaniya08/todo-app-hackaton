"""
Contract tests for Task API endpoints.

[Task]: T013, T014, T015, T026, T027, T034, T029, T030
[From]: specs/001-backend-task-api/contracts/openapi.yaml
[From]: specs/001-backend-task-api/spec.md §User Stories
[From]: specs/002-auth-jwt/spec.md §User Story 2 - Secure Task Access

These tests verify that API endpoints match the contract specification exactly.
Tests are written FIRST (TDD red phase) before implementation.
"""

import pytest
from fastapi.testclient import TestClient
from src.models.user import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)


class TestCreateTask:
    """Contract tests for POST /api/{user_id}/tasks endpoint."""

    def test_create_task_valid_data(self, authenticated_client: TestClient, test_user: User):
        """Test creating a task with valid data returns 201."""
        response = authenticated_client.post(
            f"/api/{test_user.id}/tasks",
            json={"title": "Buy groceries", "description": "Milk, eggs, bread"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Buy groceries"
        assert data["description"] == "Milk, eggs, bread"
        assert data["user_id"] == test_user.id
        assert data["completed"] is False
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_task_without_description(self, authenticated_client: TestClient, test_user: User):
        """Test creating a task without description returns 201."""
        response = authenticated_client.post(
            f"/api/{test_user.id}/tasks",
            json={"title": "Call dentist"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Call dentist"
        assert data["description"] is None
        assert data["user_id"] == test_user.id

    def test_create_task_empty_title(self, authenticated_client: TestClient, test_user: User):
        """Test creating a task with empty title returns 422."""
        response = authenticated_client.post(
            f"/api/{test_user.id}/tasks",
            json={"title": "", "description": "Test"},
        )
        assert response.status_code == 422

    def test_create_task_whitespace_title(self, authenticated_client: TestClient, test_user: User):
        """Test creating a task with whitespace-only title returns 422."""
        response = authenticated_client.post(
            f"/api/{test_user.id}/tasks",
            json={"title": "   ", "description": "Test"},
        )
        assert response.status_code == 422

    def test_create_task_title_too_long(self, authenticated_client: TestClient, test_user: User):
        """Test creating a task with title >200 chars returns 400."""
        long_title = "A" * 201
        response = authenticated_client.post(
            f"/api/{test_user.id}/tasks",
            json={"title": long_title, "description": "Test"},
        )
        assert response.status_code == 422  # Pydantic validation error

    def test_create_task_description_too_long(self, authenticated_client: TestClient, test_user: User):
        """Test creating a task with description >1000 chars returns 400."""
        long_description = "A" * 1001
        response = authenticated_client.post(
            f"/api/{test_user.id}/tasks",
            json={"title": "Test", "description": long_description},
        )
        assert response.status_code == 422  # Pydantic validation error

    def test_create_task_missing_title(self, authenticated_client: TestClient, test_user: User):
        """Test creating a task without title returns 422."""
        response = authenticated_client.post(
            f"/api/{test_user.id}/tasks",
            json={"description": "Test"},
        )
        assert response.status_code == 422  # Pydantic validation error


class TestListTasks:
    """Contract tests for GET /api/{user_id}/tasks endpoint."""

    def test_list_tasks_returns_array(self, authenticated_client: TestClient, test_user: User):
        """Test listing tasks returns an array."""
        # Create a task first
        authenticated_client.post(
            f"/api/{test_user.id}/tasks",
            json={"title": "Task 1", "description": "Description 1"},
        )

        response = authenticated_client.get(f"/api/{test_user.id}/tasks")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_list_tasks_empty(self, authenticated_client: TestClient, test_user: User):
        """Test listing tasks for user with no tasks returns empty array."""
        response = authenticated_client.get(f"/api/{test_user.id}/tasks")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_list_tasks_user_isolation(self, authenticated_client: TestClient, test_user: User, session):
        """Test that users can only see their own tasks."""
        # Create tasks for test_user
        authenticated_client.post(
            f"/api/{test_user.id}/tasks",
            json={"title": "Test User Task 1"},
        )
        authenticated_client.post(
            f"/api/{test_user.id}/tasks",
            json={"title": "Test User Task 2"},
        )

        # Create another user with tasks
        from src.models.user import User
        other_user = User(
            id="other-user-456",
            email="other@example.com",
            password_hash=pwd_context.hash("password"),
            name="Other User",
        )
        session.add(other_user)
        session.commit()

        from src.models.task import Task
        other_task = Task(user_id=other_user.id, title="Other User Task", completed=False)
        session.add(other_task)
        session.commit()

        # Get tasks for test_user - should only see their own
        response = authenticated_client.get(f"/api/{test_user.id}/tasks")
        assert response.status_code == 200
        user_tasks = response.json()
        assert len(user_tasks) == 2
        for task in user_tasks:
            assert task["user_id"] == test_user.id

    def test_list_tasks_ordered_by_created_at_desc(self, authenticated_client: TestClient, test_user: User):
        """Test that tasks are returned in descending order by creation date."""
        # Create multiple tasks
        authenticated_client.post(f"/api/{test_user.id}/tasks", json={"title": "Task 1"})
        authenticated_client.post(f"/api/{test_user.id}/tasks", json={"title": "Task 2"})
        authenticated_client.post(f"/api/{test_user.id}/tasks", json={"title": "Task 3"})

        response = authenticated_client.get(f"/api/{test_user.id}/tasks")
        assert response.status_code == 200
        tasks = response.json()

        # Verify newest task is first
        assert tasks[0]["title"] == "Task 3"
        assert tasks[-1]["title"] == "Task 1"


class TestGetTask:
    """Contract tests for GET /api/{user_id}/tasks/{id} endpoint."""

    def test_get_task_returns_task(self, authenticated_client: TestClient, test_user: User):
        """Test getting a specific task returns task details."""
        # Create a task
        create_response = authenticated_client.post(
            f"/api/{test_user.id}/tasks",
            json={"title": "Test Task", "description": "Test Description"},
        )
        task_id = create_response.json()["id"]

        # Get the task
        response = authenticated_client.get(f"/api/{test_user.id}/tasks/{task_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == task_id
        assert data["title"] == "Test Task"
        assert data["description"] == "Test Description"
        assert data["user_id"] == test_user.id

    def test_get_task_not_found(self, authenticated_client: TestClient, test_user: User):
        """Test getting a non-existent task returns 404."""
        response = authenticated_client.get(f"/api/{test_user.id}/tasks/99999")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    def test_get_task_wrong_user(self, authenticated_client: TestClient, test_user: User, session):
        """Test getting another user's task returns 404."""
        # Create another user with a task
        from src.models.user import User
        other_user = User(
            id="other-user-789",
            email="other2@example.com",
            password_hash=pwd_context.hash("password"),
            name="Other User",
        )
        session.add(other_user)
        session.commit()

        from src.models.task import Task
        other_task = Task(user_id=other_user.id, title="Other User Task", completed=False)
        session.add(other_task)
        session.commit()
        session.refresh(other_task)

        # Try to get the other user's task (should fail with 403 due to user_id mismatch)
        # Note: This will return 403 because the URL user_id doesn't match authenticated user
        response = authenticated_client.get(f"/api/{other_user.id}/tasks/{other_task.id}")
        assert response.status_code == 403


class TestUpdateTask:
    """Contract tests for PUT /api/{user_id}/tasks/{id} endpoint."""

    def test_update_task_valid_data(self, authenticated_client: TestClient, test_user: User):
        """Test updating a task with valid data returns 200."""
        # Create a task
        create_response = authenticated_client.post(
            f"/api/{test_user.id}/tasks",
            json={"title": "Original Title", "description": "Original Description"},
        )
        task_id = create_response.json()["id"]

        # Update the task
        response = authenticated_client.put(
            f"/api/{test_user.id}/tasks/{task_id}",
            json={"title": "Updated Title", "description": "Updated Description"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == task_id
        assert data["title"] == "Updated Title"
        assert data["description"] == "Updated Description"
        assert data["user_id"] == test_user.id

    def test_update_task_not_found(self, authenticated_client: TestClient, test_user: User):
        """Test updating a non-existent task returns 404."""
        response = authenticated_client.put(
            f"/api/{test_user.id}/tasks/99999",
            json={"title": "Updated Title"},
        )
        assert response.status_code == 404

    def test_update_task_wrong_user(self, authenticated_client: TestClient, test_user: User, session):
        """Test updating another user's task returns 403."""
        # Create another user with a task
        from src.models.user import User
        other_user = User(
            id="other-user-update",
            email="other-update@example.com",
            password_hash=pwd_context.hash("password"),
            name="Other User",
        )
        session.add(other_user)
        session.commit()

        from src.models.task import Task
        other_task = Task(user_id=other_user.id, title="Other User Task", completed=False)
        session.add(other_task)
        session.commit()
        session.refresh(other_task)

        # Try to update as different user (should get 403)
        response = authenticated_client.put(
            f"/api/{other_user.id}/tasks/{other_task.id}",
            json={"title": "Hacked Title"},
        )
        assert response.status_code == 403

    def test_update_task_invalid_data(self, authenticated_client: TestClient, test_user: User):
        """Test updating a task with invalid data returns 422."""
        # Create a task
        create_response = authenticated_client.post(
            f"/api/{test_user.id}/tasks",
            json={"title": "Test Task"},
        )
        task_id = create_response.json()["id"]

        # Try to update with empty title
        response = authenticated_client.put(
            f"/api/{test_user.id}/tasks/{task_id}",
            json={"title": ""},
        )
        assert response.status_code == 422


class TestDeleteTask:
    """Contract tests for DELETE /api/{user_id}/tasks/{id} endpoint."""

    def test_delete_task(self, authenticated_client: TestClient, test_user: User):
        """Test deleting a task returns 204."""
        # Create a task
        create_response = authenticated_client.post(
            f"/api/{test_user.id}/tasks",
            json={"title": "Task to Delete"},
        )
        task_id = create_response.json()["id"]

        # Delete the task
        response = authenticated_client.delete(f"/api/{test_user.id}/tasks/{task_id}")
        assert response.status_code == 204

        # Verify task is deleted
        get_response = authenticated_client.get(f"/api/{test_user.id}/tasks/{task_id}")
        assert get_response.status_code == 404

    def test_delete_task_not_found(self, authenticated_client: TestClient, test_user: User):
        """Test deleting a non-existent task returns 404."""
        response = authenticated_client.delete(f"/api/{test_user.id}/tasks/99999")
        assert response.status_code == 404

    def test_delete_task_wrong_user(self, authenticated_client: TestClient, test_user: User, session):
        """Test deleting another user's task returns 403."""
        # Create another user with a task
        from src.models.user import User
        other_user = User(
            id="other-user-delete",
            email="other-delete@example.com",
            password_hash=pwd_context.hash("password"),
            name="Other User",
        )
        session.add(other_user)
        session.commit()

        from src.models.task import Task
        other_task = Task(user_id=other_user.id, title="Other User Task", completed=False)
        session.add(other_task)
        session.commit()
        session.refresh(other_task)

        # Try to delete as different user (should get 403)
        response = authenticated_client.delete(f"/api/{other_user.id}/tasks/{other_task.id}")
        assert response.status_code == 403


class TestToggleCompletion:
    """Contract tests for PATCH /api/{user_id}/tasks/{id}/complete endpoint."""

    def test_toggle_completion_incomplete_to_complete(self, authenticated_client: TestClient, test_user: User):
        """Test toggling an incomplete task to complete returns 200."""
        # Create a task (default: incomplete)
        create_response = authenticated_client.post(
            f"/api/{test_user.id}/tasks",
            json={"title": "Task to Complete"},
        )
        task_id = create_response.json()["id"]
        assert create_response.json()["completed"] is False

        # Toggle to complete
        response = authenticated_client.patch(f"/api/{test_user.id}/tasks/{task_id}/complete")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == task_id
        assert data["completed"] is True

    def test_toggle_completion_complete_to_incomplete(self, authenticated_client: TestClient, test_user: User):
        """Test toggling a complete task to incomplete returns 200."""
        # Create and complete a task
        create_response = authenticated_client.post(
            f"/api/{test_user.id}/tasks",
            json={"title": "Task to Toggle"},
        )
        task_id = create_response.json()["id"]

        # Toggle to complete
        authenticated_client.patch(f"/api/{test_user.id}/tasks/{task_id}/complete")

        # Toggle back to incomplete
        response = authenticated_client.patch(f"/api/{test_user.id}/tasks/{task_id}/complete")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == task_id
        assert data["completed"] is False

    def test_toggle_completion_not_found(self, authenticated_client: TestClient, test_user: User):
        """Test toggling a non-existent task returns 404."""
        response = authenticated_client.patch(f"/api/{test_user.id}/tasks/99999/complete")
        assert response.status_code == 404

    def test_toggle_completion_wrong_user(self, authenticated_client: TestClient, test_user: User, session):
        """Test toggling another user's task returns 403."""
        # Create another user with a task
        from src.models.user import User
        other_user = User(
            id="other-user-toggle",
            email="other-toggle@example.com",
            password_hash=pwd_context.hash("password"),
            name="Other User",
        )
        session.add(other_user)
        session.commit()

        from src.models.task import Task
        other_task = Task(user_id=other_user.id, title="Other User Task", completed=False)
        session.add(other_task)
        session.commit()
        session.refresh(other_task)

        # Try to toggle as different user (should get 403)
        response = authenticated_client.patch(f"/api/{other_user.id}/tasks/{other_task.id}/complete")
        assert response.status_code == 403


class TestSecuredTaskEndpoints:
    """
    Contract tests for secured task endpoints with JWT authentication.

    [Task]: T029
    [From]: specs/002-auth-jwt/spec.md §User Story 2 - Secure Task Access

    These tests verify that all task endpoints require valid JWT authentication
    and enforce user data isolation.
    """

    def test_list_tasks_requires_auth(self, client: TestClient):
        """Test listing tasks without authentication returns 401."""
        response = client.get("/api/user123/tasks")
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
        assert "authentication" in data["detail"].lower() or "token" in data["detail"].lower()

    def test_list_tasks_with_auth(self, authenticated_client: TestClient, test_user: User, session):
        """Test listing tasks with valid authentication returns 200."""
        # Create a task for the authenticated user
        from src.models.task import Task
        task = Task(
            user_id=test_user.id,
            title="Authenticated User Task",
            description="This task belongs to the authenticated user",
            completed=False,
        )
        session.add(task)
        session.commit()

        # List tasks with authentication
        response = authenticated_client.get(f"/api/{test_user.id}/tasks")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["user_id"] == test_user.id

    def test_list_tasks_user_isolation_with_auth(self, authenticated_client: TestClient, test_user: User, session):
        """Test that authenticated users can only see their own tasks."""
        from src.models.task import Task

        # Create another user (Alice)
        alice = User(
            id="alice-uuid-67890",
            email="alice@example.com",
            password_hash=pwd_context.hash("alicepassword"),
            name="Alice",
        )
        session.add(alice)
        session.commit()

        # Create tasks for test_user
        task1 = Task(user_id=test_user.id, title="Test User Task 1", completed=False)
        task2 = Task(user_id=test_user.id, title="Test User Task 2", completed=False)

        # Create tasks for Alice
        task3 = Task(user_id=alice.id, title="Alice Task 1", completed=False)
        task4 = Task(user_id=alice.id, title="Alice Task 2", completed=False)

        session.add_all([task1, task2, task3, task4])
        session.commit()

        # Test user lists their tasks (should only see their own)
        response = authenticated_client.get(f"/api/{test_user.id}/tasks")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        for task in data:
            assert task["user_id"] == test_user.id

    def test_create_task_requires_auth(self, client: TestClient):
        """Test creating a task without authentication returns 401."""
        response = client.post(
            "/api/user123/tasks",
            json={"title": "Unauthorized Task"},
        )
        assert response.status_code == 401

    def test_create_task_with_auth(self, authenticated_client: TestClient, test_user: User):
        """Test creating a task with valid authentication returns 201."""
        response = authenticated_client.post(
            f"/api/{test_user.id}/tasks",
            json={"title": "Authenticated Task", "description": "Created by authenticated user"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Authenticated Task"
        assert data["user_id"] == test_user.id

    def test_get_task_requires_auth(self, client: TestClient, session):
        """Test getting a task without authentication returns 401."""
        from src.models.task import Task

        # Create a task
        task = Task(user_id="user123", title="Test Task", completed=False)
        session.add(task)
        session.commit()
        session.refresh(task)

        response = client.get(f"/api/user123/tasks/{task.id}")
        assert response.status_code == 401

    def test_update_task_requires_auth(self, client: TestClient, session):
        """Test updating a task without authentication returns 401."""
        from src.models.task import Task

        # Create a task
        task = Task(user_id="user123", title="Test Task", completed=False)
        session.add(task)
        session.commit()
        session.refresh(task)

        response = client.put(
            f"/api/user123/tasks/{task.id}",
            json={"title": "Updated Title"},
        )
        assert response.status_code == 401

    def test_delete_task_requires_auth(self, client: TestClient, session):
        """Test deleting a task without authentication returns 401."""
        from src.models.task import Task

        # Create a task
        task = Task(user_id="user123", title="Test Task", completed=False)
        session.add(task)
        session.commit()
        session.refresh(task)

        response = client.delete(f"/api/user123/tasks/{task.id}")
        assert response.status_code == 401

    def test_complete_task_requires_auth(self, client: TestClient, session):
        """Test completing a task without authentication returns 401."""
        from src.models.task import Task

        # Create a task
        task = Task(user_id="user123", title="Test Task", completed=False)
        session.add(task)
        session.commit()
        session.refresh(task)

        response = client.patch(f"/api/user123/tasks/{task.id}/complete")
        assert response.status_code == 401


class TestTaskOwnership:
    """
    Contract tests for task ownership verification.

    [Task]: T030
    [From]: specs/002-auth-jwt/spec.md §User Story 2 - Secure Task Access

    These tests verify that users cannot access or modify tasks that belong
    to other users. Cross-user access should return 403 Forbidden.
    """

    def test_get_task_wrong_user_returns_403(self, authenticated_client: TestClient, test_user: User, session):
        """Test getting another user's task returns 403 Forbidden."""
        from src.models.task import Task

        # Create another user (Bob)
        bob = User(
            id="bob-uuid-99999",
            email="bob@example.com",
            password_hash=pwd_context.hash("bobpassword"),
            name="Bob",
        )
        session.add(bob)
        session.commit()

        # Create a task for Bob
        bob_task = Task(user_id=bob.id, title="Bob's Private Task", completed=False)
        session.add(bob_task)
        session.commit()
        session.refresh(bob_task)

        # Test user tries to access Bob's task (should get 403)
        response = authenticated_client.get(f"/api/{bob.id}/tasks/{bob_task.id}")
        assert response.status_code == 403
        data = response.json()
        assert "detail" in data
        assert "forbidden" in data["detail"].lower() or "access" in data["detail"].lower()

    def test_update_task_wrong_user_returns_403(self, authenticated_client: TestClient, test_user: User, session):
        """Test updating another user's task returns 403 Forbidden."""
        from src.models.task import Task

        # Create another user (Bob)
        bob = User(
            id="bob-uuid-88888",
            email="bob2@example.com",
            password_hash=pwd_context.hash("bobpassword"),
            name="Bob",
        )
        session.add(bob)
        session.commit()

        # Create a task for Bob
        bob_task = Task(user_id=bob.id, title="Bob's Task", completed=False)
        session.add(bob_task)
        session.commit()
        session.refresh(bob_task)

        # Test user tries to update Bob's task (should get 403)
        response = authenticated_client.put(
            f"/api/{bob.id}/tasks/{bob_task.id}",
            json={"title": "Hacked Title"},
        )
        assert response.status_code == 403

    def test_delete_task_wrong_user_returns_403(self, authenticated_client: TestClient, test_user: User, session):
        """Test deleting another user's task returns 403 Forbidden."""
        from src.models.task import Task

        # Create another user (Bob)
        bob = User(
            id="bob-uuid-77777",
            email="bob3@example.com",
            password_hash=pwd_context.hash("bobpassword"),
            name="Bob",
        )
        session.add(bob)
        session.commit()

        # Create a task for Bob
        bob_task = Task(user_id=bob.id, title="Bob's Task", completed=False)
        session.add(bob_task)
        session.commit()
        session.refresh(bob_task)

        # Test user tries to delete Bob's task (should get 403)
        response = authenticated_client.delete(f"/api/{bob.id}/tasks/{bob_task.id}")
        assert response.status_code == 403

    def test_complete_task_wrong_user_returns_403(self, authenticated_client: TestClient, test_user: User, session):
        """Test completing another user's task returns 403 Forbidden."""
        from src.models.task import Task

        # Create another user (Bob)
        bob = User(
            id="bob-uuid-66666",
            email="bob4@example.com",
            password_hash=pwd_context.hash("bobpassword"),
            name="Bob",
        )
        session.add(bob)
        session.commit()

        # Create a task for Bob
        bob_task = Task(user_id=bob.id, title="Bob's Task", completed=False)
        session.add(bob_task)
        session.commit()
        session.refresh(bob_task)

        # Test user tries to complete Bob's task (should get 403)
        response = authenticated_client.patch(f"/api/{bob.id}/tasks/{bob_task.id}/complete")
        assert response.status_code == 403
