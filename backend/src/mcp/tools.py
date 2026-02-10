"""
MCP tool implementations for AI Chat Agent.

[Task]: T012, T021, T025, T029, T033
[From]: specs/004-ai-chat-agent/spec.md §FR-003
[From]: specs/004-ai-chat-agent/research.md §Research Item 2
"""

import logging
from typing import Dict, Any, Optional, List
from sqlmodel import Session

from ..services.task_service import TaskService
from ..schemas.task_schemas import TaskCreate, TaskUpdate
from ..db import get_session

logger = logging.getLogger(__name__)


# OpenAI Function Tool Definitions
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "Create a new task for the user. Use this when the user wants to add, create, or remember something.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "The title or name of the task (required, max 200 chars)"
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional detailed description of the task"
                    }
                },
                "required": ["title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": "List the user's tasks. Use this when the user wants to see, view, or show their tasks.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filter": {
                        "type": "string",
                        "enum": ["all", "pending", "completed"],
                        "description": "Filter tasks by status: 'all' (default), 'pending' (incomplete), or 'completed'"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "complete_task",
            "description": "Mark a task as completed. Use this when the user wants to mark something as done or complete.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_identifier": {
                        "type": "string",
                        "description": "The title or partial title of the task to complete"
                    }
                },
                "required": ["task_identifier"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_task",
            "description": "Delete a task. Use this when the user wants to remove or delete a task.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_identifier": {
                        "type": "string",
                        "description": "The title or partial title of the task to delete"
                    }
                },
                "required": ["task_identifier"]
            }
        }
    }
]


async def add_task(args: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    """
    Create a new task for the user.

    [Task]: T021
    [From]: specs/004-ai-chat-agent/spec.md §User Story 2

    Args:
        args: Tool arguments (title, description)
        user_id: Authenticated user ID

    Returns:
        Dict with created task details
    """
    title = args.get("title", "").strip()
    description = args.get("description")

    if not title:
        return {"error": "Task title is required"}

    if len(title) > 200:
        title = title[:200]

    logger.info(f"Creating task for user={user_id}: {title}")

    try:
        # Get a database session
        session_gen = get_session()
        session = next(session_gen)

        try:
            task_data = TaskCreate(title=title, description=description)
            task = TaskService.create_task(session, user_id, task_data)

            return {
                "success": True,
                "task_id": task.id,
                "title": task.title,
                "description": task.description,
                "created_at": task.created_at.isoformat()
            }
        finally:
            session.close()

    except Exception as e:
        logger.error(f"Failed to create task: {e}", exc_info=True)
        return {"error": f"Failed to create task: {str(e)}"}


async def list_tasks(args: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    """
    List tasks for the user.

    [Task]: T025, T028
    [From]: specs/004-ai-chat-agent/spec.md §User Story 3

    Args:
        args: Tool arguments (filter)
        user_id: Authenticated user ID

    Returns:
        Dict with task list
    """
    filter_type = args.get("filter", "all")

    logger.info(f"Listing tasks for user={user_id}, filter={filter_type}")

    try:
        session_gen = get_session()
        session = next(session_gen)

        try:
            tasks = TaskService.list_tasks(session, user_id)

            # Apply filter
            if filter_type == "pending":
                tasks = [t for t in tasks if not t.completed]
            elif filter_type == "completed":
                tasks = [t for t in tasks if t.completed]

            return {
                "success": True,
                "count": len(tasks),
                "filter": filter_type,
                "tasks": [
                    {
                        "id": t.id,
                        "title": t.title,
                        "description": t.description,
                        "completed": t.completed,
                        "created_at": t.created_at.isoformat()
                    }
                    for t in tasks
                ]
            }
        finally:
            session.close()

    except Exception as e:
        logger.error(f"Failed to list tasks: {e}", exc_info=True)
        return {"error": f"Failed to list tasks: {str(e)}"}


async def complete_task(args: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    """
    Mark a task as completed.

    [Task]: T029, T031
    [From]: specs/004-ai-chat-agent/spec.md §User Story 4

    Args:
        args: Tool arguments (task_identifier)
        user_id: Authenticated user ID

    Returns:
        Dict with completion result
    """
    task_identifier = args.get("task_identifier", "").strip().lower()

    if not task_identifier:
        return {"error": "Task identifier is required"}

    logger.info(f"Completing task for user={user_id}: {task_identifier}")

    try:
        session_gen = get_session()
        session = next(session_gen)

        try:
            # Find matching task (fuzzy match by title)
            tasks = TaskService.list_tasks(session, user_id)
            matching_task = None

            for task in tasks:
                if task_identifier in task.title.lower():
                    matching_task = task
                    break

            if not matching_task:
                return {
                    "success": False,
                    "error": f"No task found matching '{task_identifier}'"
                }

            if matching_task.completed:
                return {
                    "success": True,
                    "message": "Task is already completed",
                    "task_id": matching_task.id,
                    "title": matching_task.title
                }

            # Toggle completion
            updated_task = TaskService.toggle_completion(session, user_id, matching_task.id)

            return {
                "success": True,
                "task_id": updated_task.id,
                "title": updated_task.title,
                "completed": updated_task.completed,
                "completed_at": updated_task.updated_at.isoformat()
            }
        finally:
            session.close()

    except Exception as e:
        logger.error(f"Failed to complete task: {e}", exc_info=True)
        return {"error": f"Failed to complete task: {str(e)}"}


async def delete_task(args: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    """
    Delete a task.

    [Task]: T033, T035
    [From]: specs/004-ai-chat-agent/spec.md §User Story 5

    Args:
        args: Tool arguments (task_identifier)
        user_id: Authenticated user ID

    Returns:
        Dict with deletion result
    """
    task_identifier = args.get("task_identifier", "").strip().lower()

    if not task_identifier:
        return {"error": "Task identifier is required"}

    logger.info(f"Deleting task for user={user_id}: {task_identifier}")

    try:
        session_gen = get_session()
        session = next(session_gen)

        try:
            # Find matching task (fuzzy match by title)
            tasks = TaskService.list_tasks(session, user_id)
            matching_task = None

            for task in tasks:
                if task_identifier in task.title.lower():
                    matching_task = task
                    break

            if not matching_task:
                return {
                    "success": False,
                    "error": f"No task found matching '{task_identifier}'"
                }

            # Delete the task
            deleted = TaskService.delete_task(session, user_id, matching_task.id)

            if deleted:
                return {
                    "success": True,
                    "deleted_task_id": matching_task.id,
                    "title": matching_task.title
                }
            else:
                return {"error": "Failed to delete task"}
        finally:
            session.close()

    except Exception as e:
        logger.error(f"Failed to delete task: {e}", exc_info=True)
        return {"error": f"Failed to delete task: {str(e)}"}


async def execute_tool(tool_name: str, args: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    """
    Execute an MCP tool by name.

    [Task]: T012
    [From]: specs/004-ai-chat-agent/plan.md §Architecture Overview

    Args:
        tool_name: Name of the tool to execute
        args: Tool arguments
        user_id: Authenticated user ID

    Returns:
        Tool execution result
    """
    tool_map = {
        "add_task": add_task,
        "list_tasks": list_tasks,
        "complete_task": complete_task,
        "delete_task": delete_task,
    }

    if tool_name not in tool_map:
        logger.warning(f"Unknown tool requested: {tool_name}")
        return {"error": f"Unknown tool: {tool_name}"}

    return await tool_map[tool_name](args, user_id)
