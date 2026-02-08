"""
Unit tests for TaskService business logic.

[Task]: T041
[From]: specs/001-backend-task-api/plan.md §Testing Strategy
"""

import pytest
from sqlmodel import Session, create_engine, SQLModel
from datetime import datetime

from src.models.task import Task
from src.services.task_service import TaskService
from src.schemas.task_schemas import TaskCreate, TaskUpdate


@pytest.fixture(name="test_session")
def test_session_fixture():
    """Create a test database session."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)


class TestTaskServiceCreate:
    """Unit tests for TaskService.create_task()."""

    def test_create_task_with_description(self, test_session: Session):
        """Test creating a task with title and description."""
        task_data = TaskCreate(title="Test Task", description="Test Description")
        task = TaskService.create_task(test_session, "user123", task_data)

        assert task.id is not None
        assert task.user_id == "user123"
        assert task.title == "Test Task"
        assert task.description == "Test Description"
        assert task.completed is False
        assert isinstance(task.created_at, datetime)
        assert isinstance(task.updated_at, datetime)

    def test_create_task_without_description(self, test_session: Session):
        """Test creating a task without description."""
        task_data = TaskCreate(title="Test Task")
        task = TaskService.create_task(test_session, "user123", task_data)

        assert task.description is None
        assert task.title == "Test Task"


class TestTaskServiceList:
    """Unit tests for TaskService.list_tasks()."""

    def test_list_tasks_empty(self, test_session: Session):
        """Test listing tasks when user has no tasks."""
        tasks = TaskService.list_tasks(test_session, "user123")
        assert len(tasks) == 0

    def test_list_tasks_multiple(self, test_session: Session):
        """Test listing multiple tasks for a user."""
        # Create 3 tasks
        for i in range(3):
            task_data = TaskCreate(title=f"Task {i}")
            TaskService.create_task(test_session, "user123", task_data)

        tasks = TaskService.list_tasks(test_session, "user123")
        assert len(tasks) == 3

    def test_list_tasks_user_isolation(self, test_session: Session):
        """Test that list_tasks only returns tasks for the specified user."""
        # Create tasks for user123
        TaskService.create_task(test_session, "user123", TaskCreate(title="User123 Task"))
        # Create tasks for user456
        TaskService.create_task(test_session, "user456", TaskCreate(title="User456 Task"))

        user123_tasks = TaskService.list_tasks(test_session, "user123")
        assert len(user123_tasks) == 1
        assert user123_tasks[0].user_id == "user123"


class TestTaskServiceGet:
    """Unit tests for TaskService.get_task()."""

    def test_get_task_exists(self, test_session: Session):
        """Test getting a task that exists."""
        created_task = TaskService.create_task(
            test_session, "user123", TaskCreate(title="Test Task")
        )
        retrieved_task = TaskService.get_task(test_session, "user123", created_task.id)

        assert retrieved_task is not None
        assert retrieved_task.id == created_task.id
        assert retrieved_task.title == "Test Task"

    def test_get_task_not_found(self, test_session: Session):
        """Test getting a task that doesn't exist."""
        task = TaskService.get_task(test_session, "user123", 99999)
        assert task is None

    def test_get_task_wrong_user(self, test_session: Session):
        """Test getting a task with wrong user_id returns None."""
        created_task = TaskService.create_task(
            test_session, "user123", TaskCreate(title="Test Task")
        )
        task = TaskService.get_task(test_session, "user456", created_task.id)
        assert task is None


class TestTaskServiceUpdate:
    """Unit tests for TaskService.update_task()."""

    def test_update_task_success(self, test_session: Session):
        """Test updating a task successfully."""
        created_task = TaskService.create_task(
            test_session, "user123", TaskCreate(title="Original Title")
        )
        update_data = TaskUpdate(title="Updated Title", description="New Description")
        updated_task = TaskService.update_task(
            test_session, "user123", created_task.id, update_data
        )

        assert updated_task is not None
        assert updated_task.title == "Updated Title"
        assert updated_task.description == "New Description"

    def test_update_task_not_found(self, test_session: Session):
        """Test updating a non-existent task returns None."""
        update_data = TaskUpdate(title="Updated Title")
        result = TaskService.update_task(test_session, "user123", 99999, update_data)
        assert result is None


class TestTaskServiceDelete:
    """Unit tests for TaskService.delete_task()."""

    def test_delete_task_success(self, test_session: Session):
        """Test deleting a task successfully."""
        created_task = TaskService.create_task(
            test_session, "user123", TaskCreate(title="Test Task")
        )
        result = TaskService.delete_task(test_session, "user123", created_task.id)
        assert result is True

        # Verify task is deleted
        task = TaskService.get_task(test_session, "user123", created_task.id)
        assert task is None

    def test_delete_task_not_found(self, test_session: Session):
        """Test deleting a non-existent task returns False."""
        result = TaskService.delete_task(test_session, "user123", 99999)
        assert result is False


class TestTaskServiceToggleCompletion:
    """Unit tests for TaskService.toggle_completion()."""

    def test_toggle_completion_incomplete_to_complete(self, test_session: Session):
        """Test toggling an incomplete task to complete."""
        created_task = TaskService.create_task(
            test_session, "user123", TaskCreate(title="Test Task")
        )
        assert created_task.completed is False

        toggled_task = TaskService.toggle_completion(
            test_session, "user123", created_task.id
        )
        assert toggled_task is not None
        assert toggled_task.completed is True

    def test_toggle_completion_complete_to_incomplete(self, test_session: Session):
        """Test toggling a complete task to incomplete."""
        created_task = TaskService.create_task(
            test_session, "user123", TaskCreate(title="Test Task")
        )
        # Toggle to complete
        TaskService.toggle_completion(test_session, "user123", created_task.id)
        # Toggle back to incomplete
        toggled_task = TaskService.toggle_completion(
            test_session, "user123", created_task.id
        )
        assert toggled_task is not None
        assert toggled_task.completed is False

    def test_toggle_completion_not_found(self, test_session: Session):
        """Test toggling a non-existent task returns None."""
        result = TaskService.toggle_completion(test_session, "user123", 99999)
        assert result is None
