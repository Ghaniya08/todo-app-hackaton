"""
Task API routes.

[Task]: T020, T021, T022, T023, T032, T033, T034, T035, T036, T037, T039, T043
[From]: specs/001-backend-task-api/contracts/openapi.yaml
[From]: specs/001-backend-task-api/spec.md §API Endpoints
[From]: specs/002-auth-jwt/spec.md §User Story 2 - Secure Task Access
"""

import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlmodel import Session

from ..db import get_session
from ..schemas.task_schemas import TaskCreate, TaskUpdate, TaskResponse
from ..services.task_service import TaskService
from ..middleware.jwt_auth import verify_jwt

# Initialize logger
logger = logging.getLogger(__name__)

# Initialize router with prefix
router = APIRouter(prefix="/api/{user_id}/tasks", tags=["tasks"])


def verify_user_match(url_user_id: str, authenticated_user_id: str) -> None:
    """
    Verify that URL user_id matches authenticated user_id.

    [Task]: T039
    [From]: specs/002-auth-jwt/spec.md §FR-013

    This helper function enforces user data isolation by ensuring that
    the user_id in the URL path matches the authenticated user's ID
    extracted from the JWT token.

    Args:
        url_user_id: User ID from the URL path parameter
        authenticated_user_id: User ID extracted from JWT token

    Raises:
        HTTPException(403): If user_id mismatch (Forbidden)

    Security Note:
        Returns 403 (Forbidden) instead of 404 (Not Found) to avoid
        information leakage about resource existence.
    """
    if url_user_id != authenticated_user_id:
        logger.warning(
            f"User access violation: authenticated_user={authenticated_user_id} "
            f"attempted to access user_id={url_user_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: You can only access your own resources",
        )


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
    description="Creates a new task for the specified user",
    responses={
        201: {
            "description": "Task successfully created",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "user_id": "user123",
                        "title": "Buy groceries",
                        "description": "Milk, eggs, bread",
                        "completed": False,
                        "created_at": "2026-02-08T14:30:00Z",
                        "updated_at": "2026-02-08T14:30:00Z",
                    }
                }
            },
        },
        400: {"description": "Invalid input data"},
        401: {"description": "Missing or invalid authentication token"},
        403: {"description": "Access forbidden: Cannot create tasks for other users"},
    },
)
async def create_task(
    user_id: str = Path(..., min_length=1, max_length=255, description="User identifier"),
    task_data: TaskCreate = None,
    session: Session = Depends(get_session),
    authenticated_user_id: str = Depends(verify_jwt),
):
    """
    Create a new task.

    [Task]: T021, T033, T039, T043
    [From]: specs/001-backend-task-api/contracts/openapi.yaml POST /api/{user_id}/tasks
    [From]: specs/002-auth-jwt/spec.md §User Story 2 - Secure Task Access

    Security:
        - Requires valid JWT token (401 if missing/invalid)
        - Verifies URL user_id matches authenticated user (403 if mismatch)
        - Task is associated with authenticated user, not URL user_id
    """
    # Verify user_id in URL matches authenticated user
    verify_user_match(user_id, authenticated_user_id)

    logger.info(f"Creating task for user_id={authenticated_user_id}, title={task_data.title}")
    try:
        # Use authenticated_user_id to ensure task belongs to authenticated user
        task = TaskService.create_task(session, authenticated_user_id, task_data)
        logger.info(f"Task created successfully: task_id={task.id}, user_id={authenticated_user_id}")
        return task
    except Exception as e:
        logger.error(f"Error creating task for user_id={authenticated_user_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Service temporarily unavailable",
        )


@router.get(
    "",
    response_model=List[TaskResponse],
    status_code=status.HTTP_200_OK,
    summary="List all tasks for a user",
    description="Retrieves all tasks belonging to the specified user, ordered by creation date (newest first)",
    responses={
        200: {
            "description": "Successfully retrieved task list",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": 1,
                            "user_id": "user123",
                            "title": "Buy groceries",
                            "description": "Milk, eggs, bread",
                            "completed": False,
                            "created_at": "2026-02-08T14:30:00Z",
                            "updated_at": "2026-02-08T14:30:00Z",
                        }
                    ]
                }
            },
        },
        401: {"description": "Missing or invalid authentication token"},
        403: {"description": "Access forbidden: Cannot access other users' tasks"},
    },
)
async def list_tasks(
    user_id: str = Path(..., min_length=1, max_length=255, description="User identifier"),
    session: Session = Depends(get_session),
    authenticated_user_id: str = Depends(verify_jwt),
):
    """
    List all tasks for a user.

    [Task]: T022, T032, T039, T043
    [From]: specs/001-backend-task-api/contracts/openapi.yaml GET /api/{user_id}/tasks
    [From]: specs/002-auth-jwt/spec.md §User Story 2 - Secure Task Access

    Security:
        - Requires valid JWT token (401 if missing/invalid)
        - Verifies URL user_id matches authenticated user (403 if mismatch)
        - Returns only tasks belonging to authenticated user
    """
    # Verify user_id in URL matches authenticated user
    verify_user_match(user_id, authenticated_user_id)

    logger.info(f"Listing tasks for user_id={authenticated_user_id}")
    try:
        tasks = TaskService.list_tasks(session, authenticated_user_id)
        logger.info(f"Retrieved {len(tasks)} tasks for user_id={authenticated_user_id}")
        return tasks
    except Exception as e:
        logger.error(f"Error listing tasks for user_id={authenticated_user_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Service temporarily unavailable",
        )


@router.get(
    "/{id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a specific task",
    description="Retrieves details of a specific task by ID",
    responses={
        200: {"description": "Successfully retrieved task"},
        401: {"description": "Missing or invalid authentication token"},
        403: {"description": "Access forbidden: Cannot access other users' tasks"},
        404: {"description": "Task not found or doesn't belong to user"},
    },
)
async def get_task(
    user_id: str = Path(..., min_length=1, max_length=255, description="User identifier"),
    id: int = Path(..., ge=1, description="Task identifier"),
    session: Session = Depends(get_session),
    authenticated_user_id: str = Depends(verify_jwt),
):
    """
    Get a specific task by ID.

    [Task]: T023, T034, T039, T043
    [From]: specs/001-backend-task-api/contracts/openapi.yaml GET /api/{user_id}/tasks/{id}
    [From]: specs/002-auth-jwt/spec.md §User Story 2 - Secure Task Access

    Security:
        - Requires valid JWT token (401 if missing/invalid)
        - Verifies URL user_id matches authenticated user (403 if mismatch)
        - Service filters by authenticated user_id (404 if task not found or doesn't belong to user)
    """
    # Verify user_id in URL matches authenticated user
    verify_user_match(user_id, authenticated_user_id)

    logger.info(f"Getting task: task_id={id}, user_id={authenticated_user_id}")
    task = TaskService.get_task(session, authenticated_user_id, id)
    if not task:
        logger.warning(f"Task not found: task_id={id}, user_id={authenticated_user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    logger.info(f"Task retrieved successfully: task_id={id}, user_id={authenticated_user_id}")
    return task


@router.put(
    "/{id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a task",
    description="Updates the title and/or description of an existing task",
    responses={
        200: {"description": "Task successfully updated"},
        400: {"description": "Invalid input data"},
        401: {"description": "Missing or invalid authentication token"},
        403: {"description": "Access forbidden: Cannot update other users' tasks"},
        404: {"description": "Task not found or doesn't belong to user"},
    },
)
async def update_task(
    user_id: str = Path(..., min_length=1, max_length=255, description="User identifier"),
    id: int = Path(..., ge=1, description="Task identifier"),
    task_data: TaskUpdate = None,
    session: Session = Depends(get_session),
    authenticated_user_id: str = Depends(verify_jwt),
):
    """
    Update a task.

    [Task]: T035, T039, T043
    [From]: specs/001-backend-task-api/contracts/openapi.yaml PUT /api/{user_id}/tasks/{id}
    [From]: specs/002-auth-jwt/spec.md §User Story 2 - Secure Task Access

    Security:
        - Requires valid JWT token (401 if missing/invalid)
        - Verifies URL user_id matches authenticated user (403 if mismatch)
        - Service verifies task ownership before update (404 if not found or doesn't belong to user)
    """
    # Verify user_id in URL matches authenticated user
    verify_user_match(user_id, authenticated_user_id)

    logger.info(f"Updating task: task_id={id}, user_id={authenticated_user_id}")
    task = TaskService.update_task(session, authenticated_user_id, id, task_data)
    if not task:
        logger.warning(f"Task not found for update: task_id={id}, user_id={authenticated_user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    logger.info(f"Task updated successfully: task_id={id}, user_id={authenticated_user_id}")
    return task


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task",
    description="Permanently deletes a task",
    responses={
        204: {"description": "Task successfully deleted"},
        401: {"description": "Missing or invalid authentication token"},
        403: {"description": "Access forbidden: Cannot delete other users' tasks"},
        404: {"description": "Task not found or doesn't belong to user"},
    },
)
async def delete_task(
    user_id: str = Path(..., min_length=1, max_length=255, description="User identifier"),
    id: int = Path(..., ge=1, description="Task identifier"),
    session: Session = Depends(get_session),
    authenticated_user_id: str = Depends(verify_jwt),
):
    """
    Delete a task.

    [Task]: T036, T039, T043
    [From]: specs/001-backend-task-api/contracts/openapi.yaml DELETE /api/{user_id}/tasks/{id}
    [From]: specs/002-auth-jwt/spec.md §User Story 2 - Secure Task Access

    Security:
        - Requires valid JWT token (401 if missing/invalid)
        - Verifies URL user_id matches authenticated user (403 if mismatch)
        - Service verifies task ownership before deletion (404 if not found or doesn't belong to user)
    """
    # Verify user_id in URL matches authenticated user
    verify_user_match(user_id, authenticated_user_id)

    logger.info(f"Deleting task: task_id={id}, user_id={authenticated_user_id}")
    deleted = TaskService.delete_task(session, authenticated_user_id, id)
    if not deleted:
        logger.warning(f"Task not found for deletion: task_id={id}, user_id={authenticated_user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    logger.info(f"Task deleted successfully: task_id={id}, user_id={authenticated_user_id}")
    return None


@router.patch(
    "/{id}/complete",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Toggle task completion status",
    description="Toggles the completion status of a task (incomplete ↔ complete)",
    responses={
        200: {"description": "Task completion status successfully toggled"},
        401: {"description": "Missing or invalid authentication token"},
        403: {"description": "Access forbidden: Cannot modify other users' tasks"},
        404: {"description": "Task not found or doesn't belong to user"},
    },
)
async def toggle_task_completion(
    user_id: str = Path(..., min_length=1, max_length=255, description="User identifier"),
    id: int = Path(..., ge=1, description="Task identifier"),
    session: Session = Depends(get_session),
    authenticated_user_id: str = Depends(verify_jwt),
):
    """
    Toggle task completion status.

    [Task]: T037, T039, T043
    [From]: specs/001-backend-task-api/contracts/openapi.yaml PATCH /api/{user_id}/tasks/{id}/complete
    [From]: specs/002-auth-jwt/spec.md §User Story 2 - Secure Task Access

    Security:
        - Requires valid JWT token (401 if missing/invalid)
        - Verifies URL user_id matches authenticated user (403 if mismatch)
        - Service verifies task ownership before toggle (404 if not found or doesn't belong to user)
    """
    # Verify user_id in URL matches authenticated user
    verify_user_match(user_id, authenticated_user_id)

    logger.info(f"Toggling completion for task: task_id={id}, user_id={authenticated_user_id}")
    task = TaskService.toggle_completion(session, authenticated_user_id, id)
    if not task:
        logger.warning(f"Task not found for completion toggle: task_id={id}, user_id={authenticated_user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    logger.info(f"Task completion toggled: task_id={id}, user_id={authenticated_user_id}, completed={task.completed}")
    return task
