"""
Chat API routes for AI Chat Agent.

[Task]: T013, T039, T040
[From]: specs/004-ai-chat-agent/contracts/chat-api.yaml
[From]: specs/004-ai-chat-agent/spec.md §API Endpoints
"""

import logging
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlmodel import Session

from ..db import get_session
from ..schemas.chat_schemas import (
    ChatRequest,
    ChatResponse,
    MessageResponse,
    ToolCall,
    ConversationSummary,
)
from ..services.chat_service import ChatService
from ..services.agent_service import agent_service
from ..mcp import TOOL_DEFINITIONS, execute_tool
from ..middleware.jwt_auth import verify_jwt

# Initialize logger
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/api/{user_id}", tags=["chat"])


def verify_user_match(url_user_id: str, authenticated_user_id: str) -> None:
    """
    Verify that URL user_id matches authenticated user_id.

    [Task]: T013
    [From]: specs/004-ai-chat-agent/spec.md §FR-007
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
    "/chat",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Send a chat message to the AI agent",
    description="Sends a user message to the AI agent and returns the response. Creates a new conversation if conversation_id is not provided.",
    responses={
        200: {"description": "Successfully processed message"},
        400: {"description": "Invalid request (empty message)"},
        401: {"description": "Missing or invalid authentication token"},
        403: {"description": "Access forbidden"},
        404: {"description": "Conversation not found"},
        500: {"description": "Server error"},
    },
)
async def send_chat_message(
    user_id: str = Path(..., min_length=1, max_length=255, description="User identifier"),
    request: ChatRequest = None,
    session: Session = Depends(get_session),
    authenticated_user_id: str = Depends(verify_jwt),
):
    """
    Send a chat message to the AI agent.

    [Task]: T013
    [From]: specs/004-ai-chat-agent/spec.md §User Story 1
    """
    # Verify user_id matches authenticated user
    verify_user_match(user_id, authenticated_user_id)

    logger.info(f"Chat message from user={authenticated_user_id}, conversation={request.conversation_id}")

    try:
        # Get or create conversation
        conversation = ChatService.get_or_create_conversation(
            session,
            authenticated_user_id,
            request.conversation_id
        )

        # Verify conversation ownership if ID was provided
        if request.conversation_id and str(conversation.id) != str(request.conversation_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found",
            )

        # Store user message
        ChatService.add_message(
            session,
            conversation.id,
            "user",
            request.message
        )

        # Load conversation context
        context_messages = ChatService.get_context_messages(
            session,
            conversation.id,
            limit=20
        )

        # Register tools with agent (if not already done)
        if not agent_service.tools:
            for tool_def in TOOL_DEFINITIONS:
                agent_service.register_tool(tool_def)

        # Run agent
        result = await agent_service.run(
            messages=context_messages,
            user_id=authenticated_user_id,
            tool_executor=execute_tool
        )

        # Store assistant response
        assistant_message = ChatService.add_message(
            session,
            conversation.id,
            "assistant",
            result["content"],
            result.get("tool_calls")
        )

        # Update conversation title from first message if not set
        if not conversation.title and len(context_messages) <= 2:
            title = request.message[:50] + "..." if len(request.message) > 50 else request.message
            conversation.title = title
            session.add(conversation)
            session.commit()

        # Format response
        tool_calls = None
        if result.get("tool_calls"):
            tool_calls = [
                ToolCall(
                    tool=tc["tool"],
                    input=tc["input"],
                    output=tc.get("output")
                )
                for tc in result["tool_calls"]
            ]

        return ChatResponse(
            conversation_id=conversation.id,
            message=MessageResponse(
                id=assistant_message.id,
                role=assistant_message.role,
                content=assistant_message.content,
                tool_calls=tool_calls,
                created_at=assistant_message.created_at
            ),
            tool_calls=tool_calls
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat error for user={authenticated_user_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Service temporarily unavailable",
        )


@router.get(
    "/conversations",
    response_model=List[ConversationSummary],
    status_code=status.HTTP_200_OK,
    summary="List user's conversations",
    description="Returns a list of the user's chat conversations, ordered by most recently updated.",
)
async def list_conversations(
    user_id: str = Path(..., min_length=1, max_length=255, description="User identifier"),
    limit: int = Query(default=20, ge=1, le=100, description="Maximum number of conversations"),
    session: Session = Depends(get_session),
    authenticated_user_id: str = Depends(verify_jwt),
):
    """
    List user's conversations.

    [Task]: T039
    [From]: specs/004-ai-chat-agent/contracts/chat-api.yaml
    """
    verify_user_match(user_id, authenticated_user_id)

    logger.info(f"Listing conversations for user={authenticated_user_id}")

    try:
        conversations = ChatService.list_conversations(session, authenticated_user_id, limit)
        return [
            ConversationSummary(
                id=c.id,
                title=c.title,
                created_at=c.created_at,
                updated_at=c.updated_at
            )
            for c in conversations
        ]
    except Exception as e:
        logger.error(f"Error listing conversations: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Service temporarily unavailable",
        )


@router.get(
    "/conversations/{conversation_id}/messages",
    response_model=List[MessageResponse],
    status_code=status.HTTP_200_OK,
    summary="Get messages in a conversation",
    description="Returns messages in a specific conversation, ordered chronologically.",
)
async def get_conversation_messages(
    user_id: str = Path(..., min_length=1, max_length=255, description="User identifier"),
    conversation_id: UUID = Path(..., description="Conversation identifier"),
    limit: int = Query(default=50, ge=1, le=100, description="Maximum number of messages"),
    session: Session = Depends(get_session),
    authenticated_user_id: str = Depends(verify_jwt),
):
    """
    Get messages in a conversation.

    [Task]: T040
    [From]: specs/004-ai-chat-agent/contracts/chat-api.yaml
    """
    verify_user_match(user_id, authenticated_user_id)

    logger.info(f"Getting messages for conversation={conversation_id}, user={authenticated_user_id}")

    try:
        # Verify conversation ownership
        conversation = ChatService.get_conversation(session, conversation_id, authenticated_user_id)
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found",
            )

        messages = ChatService.get_messages(session, conversation_id, authenticated_user_id, limit)
        return [
            MessageResponse(
                id=m.id,
                role=m.role,
                content=m.content,
                tool_calls=[ToolCall(**tc) for tc in m.tool_calls] if m.tool_calls else None,
                created_at=m.created_at
            )
            for m in messages
        ]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting messages: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Service temporarily unavailable",
        )
