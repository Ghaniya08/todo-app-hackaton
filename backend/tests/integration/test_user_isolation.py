"""
Integration tests for User Story 2: Secure Task Access with User Isolation.

[Task]: T031
[From]: specs/002-auth-jwt/spec.md §User Story 2

These tests verify the complete user isolation story:
- Alice creates tasks
- Bob creates tasks
- Each user can only see their own tasks
- Cross-user access attempts return 403 Forbidden
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from passlib.context import CryptContext

from src.models.user import User
from src.models.task import Task
from src.middleware.jwt_auth import create_jwt_token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)


class TestUserStory2DataIsolation:
    """
    Integration test for User Story 2: Secure Task Access with User Isolation.

    [Task]: T031
    [From]: specs/002-auth-jwt/spec.md §User Story 2

    Acceptance Criteria:
    1. Authenticated user can only see their own tasks in task list
    2. Attempting to access another user's task returns 403 Forbidden
    3. Creating a task associates it with authenticated user
    4. Updating/deleting a task verifies ownership before allowing operation
    """

    def test_user_story_2_data_isolation(self, client: TestClient, session: Session):
        """
        Complete user story test: Alice and Bob create tasks, verify isolation.

        Scenario:
        1. Alice signs up and creates 2 tasks
        2. Bob signs up and creates 2 tasks
        3. Alice lists her tasks → sees only her 2 tasks
        4. Bob lists his tasks → sees only his 2 tasks
        5. Alice tries to access Bob's task → gets 403 Forbidden
        6. Bob tries to update Alice's task → gets 403 Forbidden
        7. Alice tries to delete Bob's task → gets 403 Forbidden
        8. Bob tries to complete Alice's task → gets 403 Forbidden
        """
        # Step 1: Create Alice and Bob users
        alice = User(
            id="alice-uuid-12345",
            email="alice@example.com",
            password_hash=pwd_context.hash("alicepassword123"),
            name="Alice",
        )
        bob = User(
            id="bob-uuid-67890",
            email="bob@example.com",
            password_hash=pwd_context.hash("bobpassword123"),
            name="Bob",
        )
        session.add(alice)
        session.add(bob)
        session.commit()

        # Generate JWT tokens for Alice and Bob
        alice_token = create_jwt_token(alice.id, expires_in_hours=24)
        bob_token = create_jwt_token(bob.id, expires_in_hours=24)

        # Step 2: Alice creates 2 tasks
        alice_client = TestClient(client.app)
        alice_client.headers["Authorization"] = f"Bearer {alice_token}"

        alice_task1_response = alice_client.post(
            f"/api/{alice.id}/tasks",
            json={"title": "Alice Task 1", "description": "Alice's first task"},
        )
        assert alice_task1_response.status_code == 201
        alice_task1 = alice_task1_response.json()
        assert alice_task1["user_id"] == alice.id

        alice_task2_response = alice_client.post(
            f"/api/{alice.id}/tasks",
            json={"title": "Alice Task 2", "description": "Alice's second task"},
        )
        assert alice_task2_response.status_code == 201
        alice_task2 = alice_task2_response.json()
        assert alice_task2["user_id"] == alice.id

        # Step 3: Bob creates 2 tasks
        bob_client = TestClient(client.app)
        bob_client.headers["Authorization"] = f"Bearer {bob_token}"

        bob_task1_response = bob_client.post(
            f"/api/{bob.id}/tasks",
            json={"title": "Bob Task 1", "description": "Bob's first task"},
        )
        assert bob_task1_response.status_code == 201
        bob_task1 = bob_task1_response.json()
        assert bob_task1["user_id"] == bob.id

        bob_task2_response = bob_client.post(
            f"/api/{bob.id}/tasks",
            json={"title": "Bob Task 2", "description": "Bob's second task"},
        )
        assert bob_task2_response.status_code == 201
        bob_task2 = bob_task2_response.json()
        assert bob_task2["user_id"] == bob.id

        # Step 4: Alice lists her tasks → should see only her 2 tasks
        alice_list_response = alice_client.get(f"/api/{alice.id}/tasks")
        assert alice_list_response.status_code == 200
        alice_tasks = alice_list_response.json()
        assert len(alice_tasks) == 2
        assert all(task["user_id"] == alice.id for task in alice_tasks)
        alice_task_titles = {task["title"] for task in alice_tasks}
        assert alice_task_titles == {"Alice Task 1", "Alice Task 2"}

        # Step 5: Bob lists his tasks → should see only his 2 tasks
        bob_list_response = bob_client.get(f"/api/{bob.id}/tasks")
        assert bob_list_response.status_code == 200
        bob_tasks = bob_list_response.json()
        assert len(bob_tasks) == 2
        assert all(task["user_id"] == bob.id for task in bob_tasks)
        bob_task_titles = {task["title"] for task in bob_tasks}
        assert bob_task_titles == {"Bob Task 1", "Bob Task 2"}

        # Step 6: Alice tries to access Bob's task → 403 Forbidden
        alice_access_bob_response = alice_client.get(
            f"/api/{bob.id}/tasks/{bob_task1['id']}"
        )
        assert alice_access_bob_response.status_code == 403
        assert "detail" in alice_access_bob_response.json()

        # Step 7: Bob tries to update Alice's task → 403 Forbidden
        bob_update_alice_response = bob_client.put(
            f"/api/{alice.id}/tasks/{alice_task1['id']}",
            json={"title": "Hacked by Bob"},
        )
        assert bob_update_alice_response.status_code == 403

        # Step 8: Alice tries to delete Bob's task → 403 Forbidden
        alice_delete_bob_response = alice_client.delete(
            f"/api/{bob.id}/tasks/{bob_task2['id']}"
        )
        assert alice_delete_bob_response.status_code == 403

        # Step 9: Bob tries to complete Alice's task → 403 Forbidden
        bob_complete_alice_response = bob_client.patch(
            f"/api/{alice.id}/tasks/{alice_task2['id']}/complete"
        )
        assert bob_complete_alice_response.status_code == 403

        # Step 10: Verify Alice can still access her own tasks
        alice_get_own_task = alice_client.get(f"/api/{alice.id}/tasks/{alice_task1['id']}")
        assert alice_get_own_task.status_code == 200
        assert alice_get_own_task.json()["id"] == alice_task1["id"]

        # Step 11: Verify Bob can still access his own tasks
        bob_get_own_task = bob_client.get(f"/api/{bob.id}/tasks/{bob_task1['id']}")
        assert bob_get_own_task.status_code == 200
        assert bob_get_own_task.json()["id"] == bob_task1["id"]

        # Step 12: Verify Alice can update her own tasks
        alice_update_own = alice_client.put(
            f"/api/{alice.id}/tasks/{alice_task1['id']}",
            json={"title": "Alice Updated Task 1", "description": "Updated by Alice"},
        )
        assert alice_update_own.status_code == 200
        assert alice_update_own.json()["title"] == "Alice Updated Task 1"

        # Step 13: Verify Bob can delete his own tasks
        bob_delete_own = bob_client.delete(f"/api/{bob.id}/tasks/{bob_task2['id']}")
        assert bob_delete_own.status_code == 204

        # Verify Bob's task is deleted
        bob_list_after_delete = bob_client.get(f"/api/{bob.id}/tasks")
        assert bob_list_after_delete.status_code == 200
        assert len(bob_list_after_delete.json()) == 1  # Only 1 task left

        # Step 14: Verify Alice's tasks are unaffected by Bob's deletion
        alice_list_final = alice_client.get(f"/api/{alice.id}/tasks")
        assert alice_list_final.status_code == 200
        assert len(alice_list_final.json()) == 2  # Still has 2 tasks

    def test_user_cannot_list_another_users_tasks(self, client: TestClient, session: Session):
        """
        Test that a user cannot list another user's tasks by changing the URL.

        [Task]: T031
        [From]: specs/002-auth-jwt/spec.md §FR-013

        Scenario:
        1. Alice is authenticated
        2. Alice tries to list Bob's tasks by using /api/{bob_id}/tasks
        3. Request should be rejected with 403 Forbidden
        """
        # Create Alice and Bob
        alice = User(
            id="alice-uuid-99999",
            email="alice2@example.com",
            password_hash=pwd_context.hash("alicepassword"),
            name="Alice",
        )
        bob = User(
            id="bob-uuid-88888",
            email="bob2@example.com",
            password_hash=pwd_context.hash("bobpassword"),
            name="Bob",
        )
        session.add(alice)
        session.add(bob)
        session.commit()

        # Create tasks for Bob
        bob_task = Task(user_id=bob.id, title="Bob's Private Task", completed=False)
        session.add(bob_task)
        session.commit()

        # Alice tries to list Bob's tasks
        alice_token = create_jwt_token(alice.id, expires_in_hours=24)
        alice_client = TestClient(client.app)
        alice_client.headers["Authorization"] = f"Bearer {alice_token}"

        # Alice tries to access Bob's task list
        response = alice_client.get(f"/api/{bob.id}/tasks")
        assert response.status_code == 403
        data = response.json()
        assert "detail" in data
        assert "forbidden" in data["detail"].lower() or "access" in data["detail"].lower()

    def test_user_cannot_create_task_for_another_user(self, client: TestClient, session: Session):
        """
        Test that a user cannot create a task for another user.

        [Task]: T031
        [From]: specs/002-auth-jwt/spec.md §FR-013

        Scenario:
        1. Alice is authenticated
        2. Alice tries to create a task using /api/{bob_id}/tasks
        3. Request should be rejected with 403 Forbidden
        """
        # Create Alice and Bob
        alice = User(
            id="alice-uuid-77777",
            email="alice3@example.com",
            password_hash=pwd_context.hash("alicepassword"),
            name="Alice",
        )
        bob = User(
            id="bob-uuid-66666",
            email="bob3@example.com",
            password_hash=pwd_context.hash("bobpassword"),
            name="Bob",
        )
        session.add(alice)
        session.add(bob)
        session.commit()

        # Alice tries to create a task for Bob
        alice_token = create_jwt_token(alice.id, expires_in_hours=24)
        alice_client = TestClient(client.app)
        alice_client.headers["Authorization"] = f"Bearer {alice_token}"

        # Alice tries to create a task in Bob's namespace
        response = alice_client.post(
            f"/api/{bob.id}/tasks",
            json={"title": "Malicious Task", "description": "Created by Alice for Bob"},
        )
        assert response.status_code == 403
        data = response.json()
        assert "detail" in data
