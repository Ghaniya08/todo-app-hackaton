"""
Task service layer for business logic.

[Task]: T017, T018, T019
[From]: specs/001-backend-task-api/data-model.md §Query Patterns
[From]: specs/001-backend-task-api/spec.md §Functional Requirements
"""

from typing import List, Optional
from datetime import datetime
from sqlmodel import Session, select
from ..models.task import Task
from ..schemas.task_schemas import TaskCreate, TaskUpdate


class TaskService:
    """Service layer for task business logic."""

    @staticmethod
    def create_task(session: Session, user_id: str, task_data: TaskCreate) -> Task:
        """
        Create a new task for a user.

        Args:
            session: Database session
            user_id: User identifier
            task_data: Task creation data

        Returns:
            Task: Created task object

        [Task]: T017
        [From]: specs/001-backend-task-api/spec.md FR-003
        """
        task = Task(
            user_id=user_id,
            title=task_data.title,
            description=task_data.description,
            completed=False,
        )
        session.add(task)
        session.commit()
        session.refresh(task)
        return task

    @staticmethod
    def list_tasks(session: Session, user_id: str) -> List[Task]:
        """
        List all tasks for a user, ordered by creation date (newest first).

        Args:
            session: Database session
            user_id: User identifier

        Returns:
            List[Task]: List of tasks belonging to the user

        [Task]: T018
        [From]: specs/001-backend-task-api/spec.md FR-004
        """
        statement = (
            select(Task)
            .where(Task.user_id == user_id)
            .order_by(Task.created_at.desc())
        )
        tasks = session.exec(statement).all()
        return tasks

    @staticmethod
    def get_task(session: Session, user_id: str, task_id: int) -> Optional[Task]:
        """
        Get a specific task by ID, ensuring it belongs to the user.

        Args:
            session: Database session
            user_id: User identifier
            task_id: Task identifier

        Returns:
            Optional[Task]: Task object if found and belongs to user, None otherwise

        [Task]: T019
        [From]: specs/001-backend-task-api/spec.md FR-005, FR-009
        """
        statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        task = session.exec(statement).first()
        return task

    @staticmethod
    def update_task(
        session: Session, user_id: str, task_id: int, task_data: TaskUpdate
    ) -> Optional[Task]:
        """
        Update a task's title and description.

        Args:
            session: Database session
            user_id: User identifier
            task_id: Task identifier
            task_data: Task update data

        Returns:
            Optional[Task]: Updated task object if found, None otherwise
        """
        task = TaskService.get_task(session, user_id, task_id)
        if task:
            task.title = task_data.title
            task.description = task_data.description
            task.updated_at = datetime.utcnow()
            session.add(task)
            session.commit()
            session.refresh(task)
        return task

    @staticmethod
    def delete_task(session: Session, user_id: str, task_id: int) -> bool:
        """
        Delete a task.

        Args:
            session: Database session
            user_id: User identifier
            task_id: Task identifier

        Returns:
            bool: True if task was deleted, False if not found
        """
        task = TaskService.get_task(session, user_id, task_id)
        if task:
            session.delete(task)
            session.commit()
            return True
        return False

    @staticmethod
    def toggle_completion(
        session: Session, user_id: str, task_id: int
    ) -> Optional[Task]:
        """
        Toggle a task's completion status.

        Args:
            session: Database session
            user_id: User identifier
            task_id: Task identifier

        Returns:
            Optional[Task]: Updated task object if found, None otherwise
        """
        task = TaskService.get_task(session, user_id, task_id)
        if task:
            task.completed = not task.completed
            task.updated_at = datetime.utcnow()
            session.add(task)
            session.commit()
            session.refresh(task)
        return task
